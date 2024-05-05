import lark

from .context import Context
from .utils import *


def visit_empty(node: lark.tree.Tree, context: Context):
    tokens = []
    return tokens


def visit_optional_fraction(node: lark.tree.Tree, context: Context):
    return node.children[0].value


def visit_num(node: lark.tree.Tree, context: Context):
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


def visit_period(node: lark.tree.Tree, context: Context):
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


def visit_basic_type(node: lark.tree.Tree, context: Context):
    return type_map[node.children[0].value]


def visit_type(node: lark.tree.Tree, context: Context):
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
    if name == func_name:
        return "_" + name
    else:
        return node.children[0].value


def visit_idlist(node: lark.tree.Tree, context: Context):
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


def visit_value_parameter(node: lark.tree.Tree, context: Context):
    ids = []
    type_ = None
    for child in node.children:
        if child.data == "idlist":
            # 函数形参不需要考虑名称修正
            # ids = visit_idlist(child, context, None)
            ids = visit_idlist(child, context)
        elif child.data == "basic_type":
            type_ = visit_basic_type(child, context)
        else:
            raise Exception("Unknown value_parameter child data: {}".format(child.data))
    return {"ids": ids, "type": type_}


def visit_var_parameter(node: lark.tree.Tree, context: Context):
    tokens = []
    value_parameter = visit_value_parameter(node.children[0], context)
    first = True
    for id in value_parameter["ids"]:
        if first:
            first = False
        else:
            tokens.append(",")
        id_type = value_parameter["type"]
        context.register_value(id, id_type, True)
        tokens.append(id_type)
        tokens.append(id)
    return tokens


def visit_parameter(node: lark.tree.Tree, context: Context):
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
                id_type = value_parameter["type"]
                context.register_value(id, id_type, True)
                tokens.append(id_type)
                tokens.append(id)
        else:
            raise Exception("Unknown parameter child data: {}".format(child.data))
    return tokens


def visit_parameter_list(node: lark.tree.Tree, context: Context):
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


def visit_formal_parameter(node: lark.tree.Tree, context: Context):
    tokens = ["("]
    parameter_list = visit_parameter_list(node.children[0], context)
    tokens.extend(parameter_list)
    tokens.append(")")
    return tokens


def visit_subprogram_head(node: lark.tree.Tree, context: Context):
    tokens = []
    basic_type = None
    id_ = None
    formal_parameter = None
    for child in node.children:
        if child.data == "basic_type":
            basic_type = visit_basic_type(child, context)
        elif child.data == "id":
            # subprogram_head中的id不需要考虑func_name修正
            id_ = visit_id(child, context, None)
        elif child.data == "formal_parameter":
            formal_parameter = visit_formal_parameter(child, context)
        else:
            raise Exception("Unknown subprogram_head child data: {}".format(child.data))
    if basic_type:
        tokens.append(basic_type)
    else:
        tokens.append("void")
    tokens.append(id_)
    tokens.extend(formal_parameter)
    context.register_func(id_, tokens, None)
    return tokens


def visit_func_id(node, context, func_name):
    tokens = []
    for child in node.children:
        assert child.data == "id"
        for grandchild in child.children:
            if grandchild.type == "IDENTIFIER_TOKEN":
                tokens.append(grandchild.value)
            else:
                raise Exception("Unknown func_id grandchild type: {}".format(grandchild.type))
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
    isArray = False
    id_varpart = None
    variable_type = None
    id_token = None
    for child in node.children:
        if child.data == "id":
            id_token = visit_id(child, context, func_name)
        elif child.data == "id_varpart":
            id_varpart = visit_id_varpart(child, context, func_name)
            if len(id_varpart) > 0:
                isArray = True
        else:
            raise Exception("Unknown variable child data: {}".format(child.data))
    values = context.get_values()
    if isArray:
        array = context.get_array(id_token)
        variable_type = array.type
    else:
        value = context.get_value(id_token)
        variable_type = value.type
    tokens.append(id_token)
    tokens.extend(id_varpart)
    return tokens, variable_type


def visit_variable_list(node, context, func_name):
    tokens = []
    first = True
    for child in node.children:
        if first:
            first = False
        else:
            tokens.append(",")
        variable_token, variable_type = visit_variable(child, context, func_name)
        tokens.extend(variable_token)
    return tokens


def visit_function_call(node, context, func_name):
    tokens = []
    function_type = None
    for child in node.children:
        if child.data == "func_id":
            function_token = visit_func_id(child, context, func_name)
            function_name = function_token[0]
            functions = context.get_funcs()
            function = context.get_func(function_name)
            function_type = function.header[0]
            tokens.extend(function_token)
        elif child.data == "expression_list":
            tokens.append("(")
            expression_list_tokens = ""
            expression_list_tokens = visit_expression_list(child, context, func_name)
            tokens.extend(expression_list_tokens)
            tokens.append(")")
        else:
            raise Exception("Unknown procedure_call child data: {}".format(child.data))

    return tokens, function_type


def visit_factor(node, context, func_name):
    tokens = []
    factor_type = None
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            token_type = child.type
            token_value = child.value
            if token_type == "NOT":
                tokens.append("!")
            elif token_type == "UMINUS":
                tokens.append(uminus_map[token_value])
        elif child.data == "num":
            num_token, factor_type = visit_num(child, context)
            tokens.extend(num_token)
        elif child.data == "expression":
            tokens.append("(")
            expression_token, expression_type = visit_expression(child, context, func_name)
            tokens.extend(expression_token)
            tokens.append(")")
            factor_type = expression_type
        elif child.data == "factor":
            factor_token, factor_type = visit_factor(child, context, func_name)
            tokens.extend(factor_token)
        elif child.data == "variable":
            variable_token, factor_type = visit_variable(child, context, func_name)
            tokens.extend(variable_token)
        elif child.data == "function_call":
            function_call_token, factor_type = visit_function_call(child, context, func_name)
            tokens.extend(function_call_token)
        else:
            raise Exception("Unknown factor child data: {}".format(child.data))
    return tokens, factor_type


def visit_term(node, context, func_name):
    term_type = None
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(mulop_map[child.value])
        elif child.data == "factor":
            factor_token, factor_type = visit_factor(child, context, func_name)
            tokens.extend(factor_token)
            term_type = factor_type
        elif child.data == "term":
            term_token, term_type = visit_term(child, context, func_name)
            tokens.extend(term_token)
        else:
            raise Exception("Unknown term child data: {}".format(child.data))
    return tokens, term_type


def visit_simple_expression(node, context, func_name):
    tokens = []
    simple_expression_type = None
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(addop_map[child.value])
        elif child.data == "term":
            term_token, term_type = visit_term(child, context, func_name)
            tokens.extend(term_token)
            simple_expression_type = term_type
        elif child.data == "simple_expression":
            simple_expression_token, simple_expression_type = visit_simple_expression(child, context, func_name)
            tokens.extend(simple_expression_token)
        else:
            raise Exception(
                "Unknown simple_expression child data: {}".format(child.data)
            )
    return tokens, simple_expression_type


def visit_expression(node, context, func_name):
    tokens = []
    expression_type = None
    isBool = False
    simple_expression_type = None
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(relop_map[child.value])
            isBool = True
        elif child.data == "simple_expression":
            simple_expression_token, simple_expression_type = visit_simple_expression(child, context, func_name)
            tokens.extend(simple_expression_token)
        else:
            raise Exception("Unknown expression child data: {}".format(child.data))
    if isBool:
        expression_type = "bool"
    else:
        expression_type = simple_expression_type
    return tokens, expression_type


def visit_expression_list(node, context, func_name):
    tokens = []
    first = True
    for child in node.children:
        if first:
            first = False
        else:
            tokens.append(",")
        expression_tokens, _ = visit_expression(child, context, func_name)
        tokens.extend(expression_tokens)
    # test if all members of tokens are string
    for token in tokens:
        if not isinstance(token, str):
            raise Exception("Token is not string: {}".format(token))
    return tokens


def visit_assign_statement(node, context, func_name):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(assignop_map[child.value])
        elif child.data == "expression":
            expression_tokens, _ = visit_expression(child, context, func_name)
            tokens.extend(expression_tokens)
        elif child.data == "variable":
            variable_tokens, variable_type = visit_variable(child, context, func_name)
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
            expression_tokens, expression_type = visit_expression(child, context, func_name)
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
    tokens = []
    ids = []
    types = []
    for child in node.children:
        if child.data == "expression":
            expression_tokens, expression_type = visit_expression(child, context, func_name)
            assert len(expression_tokens) == 1
            id_ = expression_tokens[0]
            ids.append(id_)
            value = context.get_value(id_)
            types.append(value.type)
        else:
            raise Exception("Unknown read_params child data: {}".format(child.data))
    format_ = types_to_format(types)
    tokens.append(format_)
    for id_ in ids:
        tokens.append(",")
        tokens.append("&")
        tokens.append(id_)
    return tokens


def types_to_format(types):
    format_ = '"'
    for id_type in types:
        if id_type == "int":
            format_ += r"%d"
        elif id_type == "float":
            format_ += r"%f"
        elif id_type == "char":
            format_ += r"%c"
        else:
            raise Exception("Unknown type: {}".format(id_type))
    format_ += '"'
    return format_


def construct_write_params(node, context, func_name):
    tokens = []
    expressions = []
    types = []
    for child in node.children:
        if child.data == "expression":
            expression_token, expression_type = visit_expression(child, context, func_name)
            expressions.append(expression_token)
            types.append(expression_type)
        else:
            raise Exception("Unknown write_params child data: {}".format(child.data))
    format_ = types_to_format(types)
    tokens.append(format_)
    for expression in expressions:
        tokens.append(",")
        tokens.extend(expression)
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
            if isRead:
                expression_list_tokens = construct_read_params(
                    child, context, func_name
                )
            elif isWrite:
                expression_list_tokens = construct_write_params(
                    child, context, func_name
                )
            else:
                expression_list_tokens = visit_expression_list(
                    child, context, func_name
                )
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
    statement_list_tokens = visit_statement_list(node.children[0], context, func_name)
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
    tokens.extend(["for", "("])
    tokens.extend(id_tokens)
    tokens.append("=")
    tokens.extend(from_tokens)
    tokens.append(";")
    tokens.extend(id_tokens)
    tokens.append("<=")
    tokens.extend(to_tokens)
    tokens.append(";")
    tokens.extend(id_tokens)
    tokens.extend(["++", ")"])
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
            compound_statement_tokens = visit_compound_statement(
                child, context, func_name
            )
            tokens.append("{")
            tokens.extend(compound_statement_tokens)
            tokens.append("}")
        elif child.data == "if_else_statement":
            if_else_statement_tokens = visit_if_else_statement(
                child, context, func_name
            )
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
    if len(tokens) > 0 and tokens[-1] != ";":
        tokens.append(";")
    return tokens


def visit_const_value(node: lark.tree.Tree, context: Context):
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


def visit_const_declaration(node: lark.tree.Tree, context: Context):
    tokens = []
    for child in node.children:
        id = ""
        if child.data == "id":
            tokens.append("const")
            # 定义const_declaration时不进行id修正
            id = visit_id(child, context, None)
        elif child.data == "const_value":
            res = visit_const_value(
                child, context
            )  # [123.456, "float"] 或 ["test", "char*"] ...
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


def visit_const_declarations(node: lark.tree.Tree, context: Context):
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


def visit_var_declaration(node: lark.tree.Tree, context: Context):
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


def visit_var_declarations(node: lark.tree.Tree, context: Context):
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


def visit_program_head(node: lark.tree.Tree, context: Context):
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
    tokens = ['#include "mp2c.h"']
    return tokens


def visit_subprogram_body(node, context, subprogram_head_tokens):
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
    return tokens


def visit_subprogram(node: lark.tree.Tree, context: Context):
    context.enter_scope()
    tokens = []
    subprogram_head_tokens = []
    subprogram_body_tokens = []
    for child in node.children:
        if child.data == "subprogram_head":
            subprogram_head_tokens = visit_subprogram_head(child, context)
        elif child.data == "subprogram_body":
            subprogram_body_tokens = visit_subprogram_body(
                child, context, subprogram_head_tokens
            )
        else:
            raise Exception("Unknown subprogram child data: {}".format(child.data))
    ret_type = subprogram_head_tokens[0]
    function_name = subprogram_head_tokens[1]
    function_header = subprogram_head_tokens
    function_tokens = ["{", ret_type, "_" + function_name, ";"]
    function_tokens.extend(subprogram_body_tokens)
    function_tokens.append("return")
    function_tokens.append("_" + function_name)
    function_tokens.append(";")
    function_tokens.append("}")
    context.declare_func(function_name, function_tokens)
    context.exit_scope()
    return tokens


def visit_subprogram_declarations(node: lark.tree.Tree, context: Context):
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


def visit_program_body(node: lark.tree.Tree, context: Context):
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
    return tokens


def visit_programstruct(node: lark.tree.Tree, context: Context):
    # 进入全局作用域
    context.enter_scope()
    tokens = []
    program_head_tokens = []
    program_body_tokens = []
    for child in node.children:
        if child.data == "program_head":
            program_head_tokens = visit_program_head(child, context)
        elif child.data == "program_body":
            program_body_tokens = visit_program_body(child, context)
        else:
            raise Exception("Unknown programstruct child data: {}".format(child.data))
    tokens.extend(program_head_tokens)
    functions = context.get_funcs()
    for function in functions:
        tokens.extend(functions[function].header)
        tokens.append(";")
    tokens.extend(program_body_tokens)
    for function in functions:
        tokens.extend(functions[function].header)
        tokens.extend(functions[function].tokens)
    context.exit_scope()

    return tokens
