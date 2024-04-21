import lark
from .utils import *
from .context import Context, MiniPascalFunction


def visit_empty(node, context):
    tokens = []
    return tokens


def visit_optional_fraction(node, context):
    return node.children[0].value


def visit_num(node, context):
    tokens = []
    typename = ""
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            typename = "int"
            tokens.append(child.value)

        elif child.data == "optional_fraction":
            typename = "float"
            optional_fraction_part = visit_optional_fraction(child, context)
            tokens[-1] += "."
            tokens[-1] += optional_fraction_part
        else:
            raise Exception("Unknown num child data: {}".format(child.data))

    return [tokens, typename]


def visit_period(node, context):
    periods = []
    current_period = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            current_period.append(int(child.value))
        elif child.data == "period":
            current_period = visit_period(child, context)
            periods.append(current_period)
            current_period = []
        else:
            raise Exception("Unknown period child data: {}".format(child.data))
    periods.append(current_period)
    return periods


def visit_basic_type(node, context):
    return type_map[node.children[0].value]


def visit_type(node, context):
    type = {"basic_type": None, "is_array": False, "period": []}
    for child in node.children:
        if child.data == "basic_type":
            type["basic_type"] = visit_basic_type(child, context)
        elif child.data == "period":
            type["period"] = visit_period(child, context)
            type["is_array"] = True
        else:
            raise Exception("Unknown type child data: {}".format(child.data))
    return type


def visit_id(node, context, func_name):
    name = node.children[0].value
    if(name == func_name):
        return "_" + name
    else:
        return node.children[0].value


def visit_idlist(node, context):
    ids = []
    for child in node.children:
        if child.data == "id":
            # 从idlist得到的id不需要考虑func_name修正
            ids.append(visit_id(child, context, None))
        elif child.data == "idlist":
            ids.extend(visit_idlist(child, context))
        else:
            raise Exception("Unknown idlist child data: {}".format(child.data))
    return ids


def visit_value_parameter(node, context):
    ids = []
    type = None
    for child in node.children:
        if child.data == "idlist":
            # 函数形参不需要考虑名称修正
            ids = visit_idlist(child, context, None)
        elif child.data == "basic_type":
            type = visit_basic_type(child, context)
        else:
            raise Exception("Unknown value_parameter child data: {}".format(child.data))
    return {"ids": ids, "type": type}


def visit_var_parameter(node, context):
    tokens = []
    value_parameter = visit_value_parameter(node.children[0])
    first = True
    for id in value_parameter["ids"]:
        if first:
            first = False
        else:
            tokens.append(",")
        tokens.append(value_parameter["type"])
        tokens.append(id)
    return tokens


def visit_parameter(node, context):
    tokens = []
    for child in node.children:
        if child.data == "var_parameter":
            return visit_var_parameter(child, context)
        elif child.data == "value_parameter":
            value_parameter = visit_value_parameter(child, context)
            first = True
            for id in value_parameter["ids"]:
                if first:
                    first = False
                else:
                    tokens.append(",")
                tokens.append(value_parameter["type"])
                tokens.append(id)
        else:
            raise Exception("Unknown parameter child data: {}".format(child.data))
    return tokens


def visit_parameter_list(node, context):
    tokens = []
    first = True
    for child in node.children:
        assert child.data == "parameter"
        if first:
            first = False
        else:
            tokens.append(",")
        tokens.extend(visit_parameter(child, context))
    return tokens


def visit_formal_parameter(node, context):
    tokens = []
    tokens.append("(")
    parameter_list = visit_parameter_list(node.children[0],context)
    tokens.extend(parameter_list)
    tokens.append(")")
    return tokens


def visit_subprogram_head(node, context):
    tokens = []
    basic_type = None
    id = None
    formal_parameter = None
    for child in node.children:
        if child.data == "basic_type":
            basic_type = visit_basic_type(child, context)
        elif child.data == "id":
            # subprogram_head中的id不需要考虑func_name修正
            id = visit_id(child, context, None)
        elif child.data == "formal_parameter":
            formal_parameter = visit_formal_parameter(child, context)
        else:
            raise Exception("Unknown subprogram_head child data: {}".format(child.data))
    if basic_type:
        tokens.append(basic_type)
    else:
        tokens.append("void")
    tokens.append(id)
    tokens.extend(formal_parameter)
    return tokens


def visit_func_id(node, context, func_name):
    tokens = []
    for child in node.children:
        assert child.data == "id"
        id_tokens = visit_id(child, context, func_name)
        tokens.append(id_tokens)
    return tokens


def visit_id_varpart(node, context, func_name):
    tokens = []
    for child in node.children:
        if child.data == "empty":
            return tokens
        elif child.data == "expression_list":
            tokens.append("[")
            expression_list = visit_expression_list(child, context, func_name)
            tokens.extend(expression_list)
            tokens.append("]")
        else:
            raise Exception("Unknown id_varpart child data: {}".format(child.data))
    return tokens


def visit_variable(node, context, func_name):
    tokens = []
    for child in node.children:
        if child.data == "id":
            tokens.append(visit_id(child, context, func_name))
        elif child.data == "id_varpart":
            id_varpart = visit_id_varpart(child, context, func_name)
            tokens.extend(id_varpart)
        else:
            raise Exception("Unknown variable child data: {}".format(child.data))
    return tokens


def visit_variable_list(node, context, func_name):
    tokens = []
    first = True
    for child in node.children:
        if first:
            first = False
        else:
            tokens.append(",")
        tokens.extend(visit_variable(child, context, func_name))
    return tokens


def visit_factor(node, context, func_name):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            token_type = child.type
            token_value = child.value
            if token_type == "NOT":
                tokens.append("!")
            elif token_type == "UMINUS":
                tokens.append(uminus_map[token_value])
        elif child.data == "num":
            num_token = visit_num(child, context)[0]
            tokens.extend(num_token)
        elif child.data == "id":
            id_token = visit_id(child, context, func_name)
            tokens.extend(id_token)
        elif child.data == "expression":
            tokens.append("(")
            expression_token = visit_expression(child, context, func_name)
            tokens.extend(expression_token)
            tokens.append(")")
        elif child.data == "factor":
            factor_token = visit_factor(child, context, func_name)
            tokens.extend(factor_token)
        elif child.data == "func_id":
            func_id_token = visit_func_id(child, context)
            tokens.extend(func_id_token)
        elif child.data == "expression_list":
            tokens.append("(")
            expression_list_token = visit_expression_list(child, context, func_name)
            tokens.extend(expression_list_token)
            tokens.append(")")
        elif child.data == "variable":
            variable_token = visit_variable(child, context, func_name)
            tokens.extend(variable_token)
        else:
            raise Exception("Unknown factor child data: {}".format(child.data))
    return tokens


def visit_term(node, context):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(mulop_map[child.value])
        elif child.data == "factor":
            factor_token = visit_factor(child, context)
            tokens.extend(factor_token)
        elif child.data == "term":
            term_token = visit_term(child, context)
            tokens.extend(term_token)
        else:
            raise Exception("Unknown term child data: {}".format(child.data))
    return tokens


def visit_simple_expression(node, context, func_name):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(addop_map[child.value])
        elif child.data == "term":
            term_token = visit_term(child, context)
            tokens.extend(term_token)
        elif child.data == "simple_expression":
            simple_expression_token = visit_simple_expression(child, context, func_name)
            tokens.extend(simple_expression_token)
        else:
            raise Exception(
                "Unknown simple_expression child data: {}".format(child.data)
            )
    return tokens


def visit_expression(node, context, func_name):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(relop_map[child.value])
        elif child.data == "simple_expression":
            simple_expression_token = visit_simple_expression(child, context, func_name)
            tokens.extend(simple_expression_token)
        elif child.data == "expression":
            expression_token = visit_expression(child, context, func_name)
            tokens.extend(expression_token)
        else:
            raise Exception("Unknown expression child data: {}".format(child.data))
    return tokens


def visit_expression_list(node, context, func_name):
    tokens = []
    first = True
    for child in node.children:
        if first:
            first = False
        else:
            tokens.append(",")
        expression_tokens = visit_expression(child, context, func_name)
        tokens.extend(expression_tokens)
    return tokens


def visit_assign_statement(node, context, func_name):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(assignop_map[child.value])
        elif child.data == "expression":
            expression_tokens = visit_expression(child, context, func_name)
            tokens.extend(expression_tokens)
        elif child.data == "variable":
            variable_tokens = visit_variable(child, context, func_name)
            tokens.extend(variable_tokens)
        else:
            raise Exception(
                "Unknown assignment_statement child data: {}".format(child.data)
            )
    return tokens


def visit_if_else_statement(node, context, func_name):
    tokens = []
    for child in node.children:
        if child.data == "expression":
            tokens.append("if")
            tokens.append("(")
            expression_tokens = visit_expression(child, context, func_name)
            tokens.extend(expression_tokens)
            tokens.append(")")
        elif child.data == "statement":
            tokens.append("{")
            statement_tokens = visit_statement(child, context, func_name)
            tokens.extend(statement_tokens)
            tokens.append("}")
        elif child.data == "else_part":
            else_part_tokens = visit_else_part(child, context, func_name)
            tokens.extend(else_part_tokens)
        else:
            raise Exception(
                "Unknown if_else_statement child data: {}".format(child.data)
            )
    return tokens


def visit_else_part(node, context, func_name):
    tokens = []
    for child in node.children:
        if child.data == "empty":
            return tokens
        elif child.data == "statement":
            tokens.append("else")
            tokens.append("{")
            statement_tokens = visit_statement(child, context, func_name)
            tokens.extend(statement_tokens)
            tokens.append("}")
        else:
            raise Exception("Unknown else_part child data: {}".format(child.data))
    return tokens

def construct_read_params(node, context, func_name):
    # Todo : 在context.symbol_table中查询expression_list中的每个id的类型，并组织出正确的scanf参数
    tokens = []
    return tokens

def construct_write_params(node, context, func_name):
    # Todo : 在context.symbol_table中查询expression_list中的每个id的类型，并组织出正确的printf参数
    tokens = []
    return tokens  

def visit_procedure_call(node, context, func_name):
    tokens = []
    isRead = False
    isWrite = False
    for child in node.children:
        if child.data == "id":
            if child.children[0].value == "read":
                isRead = True
                tokens.append("scanf")
            elif child.children[0].value == "write":
                isWrite = True
                tokens.append("printf")
            else:
                # 过程调用不进行func_name修正
                tokens.append(visit_id(child, context, None))
        elif child.data == "expression_list":
            tokens.append("(")
            expression_list_tokens = ""
            if isRead:
                expression_list_tokens = construct_read_params(child, context, func_name)
            elif isWrite:
                expression_list_tokens = construct_write_params(child, context, func_name)
            else:
                expression_list_tokens = visit_expression_list(child, context, func_name)
            tokens.extend(expression_list_tokens)
            tokens.append(")")
        else:
            raise Exception("Unknown procedure_call child data: {}".format(child.data))
    return tokens


def visit_statement_list(node, context, func_name):
    tokens = []
    for child in node.children:
        assert child.data == "statement"
        statement_tokens = visit_statement(child, context, func_name)
        tokens.extend(statement_tokens)
        tokens.append(";")
    return tokens


def visit_compound_statement(node, context, func_name):
    tokens = []
    assert node.children[0].data == "statement_list"
    statement_list_tokens = visit_statement_list(node.children[0],context, func_name)
    tokens.extend(statement_list_tokens)
    return tokens


def visit_for_statement(node, context, func_name):
    tokens = []
    id_tokens = []
    from_tokens = []
    to_tokens = []
    statement_tokens = []
    for child in node.children:
        if child.data == "id":
            tokens.append(visit_id(child, context, func_name))
        elif child.data == "expression":
            if id_tokens:
                from_tokens = visit_expression(child, context, func_name)
            else:
                to_tokens = visit_expression(child, context, func_name)
        elif child.data == "statement":
            statement_tokens = visit_statement(child, context, func_name)
        else:
            raise Exception("Unknown for_statement child data: {}".format(child.data))
    tokens.append("for")
    tokens.append("(")
    tokens.extend(id_tokens)
    tokens.append("=")
    tokens.extend(from_tokens)
    tokens.append(";")
    tokens.extend(id_tokens)
    tokens.append("<=")
    tokens.extend(to_tokens)
    tokens.append(";")
    tokens.extend(id_tokens)
    tokens.append("++)")
    tokens.append("{")
    tokens.extend(statement_tokens)
    tokens.append("}")
    return tokens


def visit_while_statement(node, context, func_name):
    tokens = []
    for child in node.children:
        if child.data == "expression":
            tokens.append("while")
            tokens.append("(")
            expression_tokens = visit_expression(child, context, func_name)
            tokens.extend(expression_tokens)
            tokens.append(")")
        elif child.data == "statement":
            tokens.append("{")
            statement_tokens = visit_statement(child, context, func_name)
            tokens.extend(statement_tokens)
            tokens.append("}")
        else:
            raise Exception("Unknown while_statement child data: {}".format(child.data))
    return tokens


def visit_statement(node, context, func_name):
    tokens = []
    for child in node.children:
        if child.data == "procedure_call":
            procedure_call_tokens = visit_procedure_call(child, context, func_name)
            tokens.extend(procedure_call_tokens)
        elif child.data == "compound_statement":
            compound_statement_tokens = visit_compound_statement(child, context, func_name)
            tokens.append("{")
            tokens.extend(compound_statement_tokens)
            tokens.append("}")
        elif child.data == "if_else_statement":
            if_else_statement_tokens = visit_if_else_statement(child, context, func_name)
            tokens.extend(if_else_statement_tokens)
        elif child.data == "for_statement":
            for_statement_tokens = visit_for_statement(child, context, func_name)
            tokens.extend(for_statement_tokens)
        elif child.data == "while_statement":
            while_statement_tokens = visit_while_statement(child, context, func_name)
            tokens.extend(while_statement_tokens)
        elif child.data == "assign_statement":
            assign_statement_tokens = visit_assign_statement(child, context, func_name)
            tokens.extend(assign_statement_tokens)
        elif child.data == "empty":
            return tokens
        else:
            raise Exception("Unknown statement child data: {}".format(child.data))
    return tokens


def visit_const_value(node, context):
    tokens = []
    typename = ""
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            if child.type == "PLUS":
                tokens.append("+")
            elif child.type == "MINUS":
                tokens.append("-")
            elif child.type == "LETTER":
                typename = "char"
                tokens.append("'" + child.value + "'")
            else:
                raise Exception("Unknown const_value child type: {}".format(child.type))

        elif child.data == "num":
            res = visit_num(child, context)
            num_tokens = res[0]
            typename = res[1]
            tokens.extend(num_tokens)
        else:
            raise Exception("Unknown const_value child data: {}".format(child.data))

    return [tokens, typename]


def visit_const_declaration(node, context):
    tokens = []
    for child in node.children:
        id = ""
        if child.data == "id":
            tokens.append("const")
            # 定义const_declaration时不进行id修正
            id = visit_id(child, context, None)
        elif child.data == "const_value":
            res = visit_const_value(child, context) # [123.456, "float"] 或 ["test", "char*"] ...
            tokens.append(res[1])
            tokens.append(id)
            tokens.append("=")
            tokens.extend(res[0])
            tokens.append(";")
            # 符号表注册
            # type = context.cname_to_type(res[1])
            context.register_value(id, res[1], False, res[0])
        elif child.data == "const_declaration":
            tokens.extend(visit_const_declaration(child, context))
        else:
            raise Exception(
                "Unknown const_declaration child data: {}".format(child.data)
            )
    return tokens


def visit_const_declarations(node, context):
    tokens = []
    for child in node.children:
        if child.data == "const_declaration":
            tokens.extend(visit_const_declaration(child, context))
        elif child.data == "empty":
            return tokens
        else:
            raise Exception(
                "Unknown const_declarations child data: {}".format(child.data)
            )
    return tokens


def visit_var_declaration(node, context):
    tokens = []
    idlist = []
    id_type = None
    for child in node.children:
        if child.data == "idlist":
            idlist = visit_idlist(child, context)
        elif child.data == "type":
            id_type = visit_type(child, context)
        elif child.data == "var_declaration":
            tokens.extend(visit_var_declaration(child, context))
        else:
            raise Exception("Unknown var_declaration child data: {}".format(child.data))

    for id in idlist:
        tokens.append(id_type["basic_type"])
        tokens.append(id)
        
        if id_type["is_array"]:
            for period in id_type["period"]:
                tokens.append("[")
                tokens.append(str(period[0]))
                tokens.append("]")
                tokens.append("[")
                tokens.append(str(period[1]))
                tokens.append("]")
            context.register_array(id, id_type["basic_type"], id_type["period"])
        else:
            context.register_value(id, id_type["basic_type"], True)
        tokens.append(";")
    return tokens


def visit_var_declarations(node, context):
    tokens = []
    for child in node.children:
        if child.data == "var_declaration":
            tokens.extend(visit_var_declaration(child, context))
        elif child.data == "empty":
            return tokens
        else:
            raise Exception(
                "Unknown var_declarations child data: {}".format(child.data)
            )
    return tokens


def visit_program_head(node, context):
    # tokens = []
    # for child in node.children:
    #     if child.data == "id":
    #         id_tokens = visit_id(child,context)
    #         tokens.extend(id_tokens)
    #         tokens.append(";\n")
    #     elif child.data == "idlist":
    #         tokens.append("int ")
    #         idlist_tokens = visit_idlist(child,context)

    #         tokens.append(";")
    #     else:
    #         raise Exception("Unknown program_head child data: {}".format(child.data))
    tokens = ["#include \"mp2c.h\""]
    return tokens


def visit_subprogram_body(node, context, subprogram_head_tokens):
    context.enter_scope()
    func_name = subprogram_head_tokens[1]
    ret_type = subprogram_head_tokens[0]
    context.register_value("_" + func_name, ret_type, True)
    tokens = []
    for child in node.children:
        if child.data == "const_declarations":
            tokens.extend(visit_const_declarations(child, context))
        elif child.data == "var_declarations":
            tokens.extend(visit_var_declarations(child, context))
        elif child.data == "compound_statement":
            # compound_statement中如果遇到对func_name符号的引用且并非函数递归调用，则前面加一个_
            tokens.extend(visit_compound_statement(child, context, func_name))
        else:
            raise Exception("Unknown subprogram_body child data: {}".format(child.data))
    context.exit_scope()
    return tokens


def visit_subprogram(node, context):
    tokens = []
    for child in node.children:
        if child.data == "subprogram_head":
            subprogram_head_tokens = visit_subprogram_head(child, context)
        elif child.data == "subprogram_body":
            subprogram_body_tokens = visit_subprogram_body(child, context, subprogram_head_tokens)
        else:
            raise Exception("Unknown subprogram child data: {}".format(child.data))
    ret_type = subprogram_head_tokens[0]
    function_name = subprogram_head_tokens[1]
    function_header = subprogram_head_tokens
    function_tokens=["{"]
    function_tokens.append(ret_type)
    function_tokens.append("_" + function_name)
    function_tokens.append(";")

    function_tokens.extend(subprogram_body_tokens)

    function_tokens.append("return")
    function_tokens.append("_" + function_name)
    function_tokens.append(";")
    function_tokens.append("}")
    context.register_func(function_name, function_header, function_tokens)
    return tokens


def visit_subprogram_declarations(node, context):
    tokens = []
    for child in node.children:
        if child.data == "subprogram":
            tokens.extend(visit_subprogram(child, context))
        elif child.data == "subprogram_declarations":
            tokens.extend(visit_subprogram_declarations(child, context))
        elif child.data == "empty":
            return tokens
        else:
            raise Exception(
                "Unknown subprogram_declarations child data: {}".format(child.data)
            )
    return tokens


def visit_program_body(node, context):
    # 进入全局作用域
    context.enter_scope()
    tokens = []
    for child in node.children:
        if child.data == "const_declarations":
            tokens.extend(visit_const_declarations(child, context))
        elif child.data == "var_declarations":
            tokens.extend(visit_var_declarations(child, context))
        elif child.data == "subprogram_declarations":
            tokens.extend(visit_subprogram_declarations(child, context))
        elif child.data == "compound_statement":
            tokens.append("int main()")
            tokens.append("{")
            tokens.extend(visit_compound_statement(child, context, "main"))
            tokens.append("}")
        else:
            raise Exception("Unknown program_body child data: {}".format(child.data))
    # 退出全局作用域
    context.exit_scope()
    return tokens


def visit_programstruct(node, context):
    tokens = []
    for child in node.children:
        if child.data == "program_head":
            program_head_tokens=visit_program_head(child, context)
        elif child.data == "program_body":
           program_body_tokens=visit_program_body(child, context)
        else:
            raise Exception("Unknown programstruct child data: {}".format(child.data))
    tokens.extend(program_head_tokens)
    functions=context.get_funcs()
    for function in functions:
        tokens.extend(functions[function].header)
        tokens.append(";")
    tokens.extend(program_body_tokens)
    for function in functions:
        tokens.extend(functions[function].header)
        tokens.extend(functions[function].tokens)
    
    return tokens
