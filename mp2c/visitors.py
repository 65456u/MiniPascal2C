import lark
from .utils import *
from .context import Context


def visit_empty(node):
    tokens = []
    return tokens


def visit_optional_fraction(node):
    return node.children[0].value


def visit_num(node):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(child.value)
        elif child.data == "optional_fraction":
            optional_fraction_part = visit_optional_fraction(child)
            tokens[-1] += "."
            tokens[-1] += optional_fraction_part
        else:
            raise Exception("Unknown num child data: {}".format(child.data))

    return tokens


def visit_period(node):
    periods = []
    current_period = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            current_period.append(int(child.value))
        elif child.data == "period":
            current_period = visit_period(child)
            periods.append(current_period)
            current_period = []
        else:
            raise Exception("Unknown period child data: {}".format(child.data))
    periods.append(current_period)
    return periods


def visit_basic_type(node):
    return type_map[node.children[0].value]


def visit_type(node):
    type = {"basic_type": None, "is_array": False, "period": []}
    for child in node.children:
        if child.data == "basic_type":
            type["basic_type"] = visit_basic_type(child)
        elif child.data == "period":
            type["period"] = visit_period(child)
            type["is_array"] = True
        else:
            raise Exception("Unknown type child data: {}".format(child.data))
    return type


def visit_id(node):
    return node.children[0].value


def visit_idlist(node):
    ids = []
    for child in node.children:
        if child.data == "id":
            ids.append(visit_id(child))
        elif child.data == "idlist":
            ids.extend(visit_idlist(child))
        else:
            raise Exception("Unknown idlist child data: {}".format(child.data))
    return ids


def visit_value_parameter(node):
    ids = []
    type = None
    for child in node.children:
        if child.data == "idlist":
            ids = visit_idlist(child)
        elif child.data == "basic_type":
            type = visit_basic_type(child)
        else:
            raise Exception("Unknown value_parameter child data: {}".format(child.data))
    return {"ids": ids, "type": type}


def visit_var_parameter(node):
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


def visit_parameter(node):
    tokens = []
    for child in node.children:
        if child.data == "var_parameter":
            return visit_var_parameter(child)
        elif child.data == "value_parameter":
            value_parameter = visit_value_parameter(child)
            tokens.append(value_parameter["type"])
            first = True
            for id in value_parameter["ids"]:
                if first:
                    tokens.append(id)
                    first = False
                else:
                    tokens.append(",")
                    tokens.append(id)
        else:
            raise Exception("Unknown parameter child data: {}".format(child.data))
    return tokens


def visit_parameter_list(node):
    tokens = []
    first = True
    for child in node.children:
        assert child.data == "parameter"
        if first:
            first = False
        else:
            tokens.append(",")
        tokens.extend(visit_parameter(child))
    return tokens


def visit_formal_parameter(node):
    tokens = []
    tokens.append("(")
    parameter_list = visit_parameter_list(node.children[0])
    tokens.extend(parameter_list)
    tokens.append(")")
    return tokens


def visit_subprogram_head(node):
    tokens = []
    basic_type = None
    id = None
    formal_parameter = None
    for child in node.children:
        if child.data == "basic_type":
            basic_type = visit_basic_type(child)
        elif child.data == "id":
            id = visit_id(child)
        elif child.data == "formal_parameter":
            formal_parameter = visit_formal_parameter(child)
        else:
            raise Exception("Unknown subprogram_head child data: {}".format(child.data))
    if basic_type:
        tokens.append(basic_type)
    else:
        tokens.append("void")
    tokens.append(id)
    tokens.extend(formal_parameter)
    return tokens


def visit_func_id(node):
    tokens = []
    for child in node.children:
        assert child.data == "id"
        id_tokens = visit_id(child)
        tokens.append(id_tokens)
    return tokens


def visit_id_varpart(node):
    tokens = []
    for child in node.children:
        if child.data == "empty":
            return tokens
        elif child.data == "expression_list":
            tokens.append("[")
            expression_list = visit_expression_list(child)
            tokens.extend(expression_list)
            tokens.append("]")
        else:
            raise Exception("Unknown id_varpart child data: {}".format(child.data))
    return tokens


def visit_variable(node):
    tokens = []
    for child in node.children:
        if child.data == "id":
            tokens.append(visit_id(child))
        elif child.data == "id_varpart":
            id_varpart = visit_id_varpart(child)
            tokens.extend(id_varpart)
        else:
            raise Exception("Unknown variable child data: {}".format(child.data))
    return tokens


def visit_variable_list(node):
    tokens = []
    first = True
    for child in node.children:
        if first:
            first = False
        else:
            tokens.append(",")
        tokens.extend(visit_variable(child))
    return tokens


def visit_factor(node):
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
            num_token = visit_num(child)
            tokens.extend(num_token)
        elif child.data == "id":
            id_token = visit_id(child)
            tokens.extend(id_token)
        elif child.data == "expression":
            tokens.append("(")
            expression_token = visit_expression(child)
            tokens.extend(expression_token)
            tokens.append(")")
        elif child.data == "factor":
            factor_token = visit_factor(child)
            tokens.extend(factor_token)
        elif child.data == "func_id":
            func_id_token = visit_func_id(child)
            tokens.extend(func_id_token)
        elif child.data == "expression_list":
            tokens.append("(")
            expression_list_token = visit_expression_list(child)
            tokens.extend(expression_list_token)
            tokens.append(")")
        elif child.data == "variable":
            variable_token = visit_variable(child)
            tokens.extend(variable_token)
        else:
            raise Exception("Unknown factor child data: {}".format(child.data))
    return tokens


def visit_term(node):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(mulop_map[child.value])
        elif child.data == "factor":
            factor_token = visit_factor(child)
            tokens.extend(factor_token)
        elif child.data == "term":
            term_token = visit_term(child)
            tokens.extend(term_token)
        else:
            raise Exception("Unknown term child data: {}".format(child.data))
    return tokens


def visit_simple_expression(node):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(addop_map[child.value])
        elif child.data == "term":
            term_token = visit_term(child)
            tokens.extend(term_token)
        elif child.data == "simple_expression":
            simple_expression_token = visit_simple_expression(child)
            tokens.extend(simple_expression_token)
        else:
            raise Exception(
                "Unknown simple_expression child data: {}".format(child.data)
            )
    return tokens


def visit_expression(node):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(relop_map[child.value])
        elif child.data == "simple_expression":
            simple_expression_token = visit_simple_expression(child)
            tokens.extend(simple_expression_token)
        elif child.data == "expression":
            expression_token = visit_expression(child)
            tokens.extend(expression_token)
        else:
            raise Exception("Unknown expression child data: {}".format(child.data))
    return tokens


def visit_expression_list(node):
    tokens = []
    first = True
    for child in node.children:
        if first:
            first = False
        else:
            tokens.append(",")
        expression_tokens = visit_expression(child)
        tokens.extend(expression_tokens)
    return tokens


def visit_assign_statement(node):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            tokens.append(assignop_map[child.value])
        elif child.data == "expression":
            expression_tokens = visit_expression(child)
            tokens.extend(expression_tokens)
        elif child.data == "variable":
            variable_tokens = visit_variable(child)
            tokens.extend(variable_tokens)
        else:
            raise Exception(
                "Unknown assignment_statement child data: {}".format(child.data)
            )
    return tokens


def visit_if_else_statement(node):
    tokens = []
    for child in node.children:
        if child.data == "expression":
            tokens.append("if")
            tokens.append("(")
            expression_tokens = visit_expression(child)
            tokens.extend(expression_tokens)
            tokens.append(")")
        elif child.data == "statement":
            tokens.append("{")
            statement_tokens = visit_statement(child)
            tokens.extend(statement_tokens)
            tokens.append("}")
        elif child.data == "else_part":
            else_part_tokens = visit_else_part(child)
            tokens.extend(else_part_tokens)
        else:
            raise Exception(
                "Unknown if_else_statement child data: {}".format(child.data)
            )
    return tokens


def visit_else_part(node):
    tokens = []
    for child in node.children:
        if child.data == "empty":
            return tokens
        elif child.data == "statement":
            tokens.append("else")
            tokens.append("{")
            statement_tokens = visit_statement(child)
            tokens.extend(statement_tokens)
            tokens.append("}")
        else:
            raise Exception("Unknown else_part child data: {}".format(child.data))
    return tokens


def visit_procedure_call(node):
    tokens = []
    for child in node.children:
        if child.data == "id":
            tokens.append(visit_id(child))
        elif child.data == "expression_list":
            tokens.append("(")
            expression_list_tokens = visit_expression_list(child)
            tokens.extend(expression_list_tokens)
            tokens.append(")")
        else:
            raise Exception("Unknown procedure_call child data: {}".format(child.data))
    return tokens


def visit_statement_list(node):
    tokens = []
    for child in node.children:
        assert child.data == "statement"
        statement_tokens = visit_statement(child)
        tokens.extend(statement_tokens)
        tokens.append(";")
    return tokens


def visit_compound_statement(node):
    tokens = []
    tokens.append("{")
    assert node.children[0].data == "statement_list"
    statement_list_tokens = visit_statement_list(node.children[0])
    tokens.extend(statement_list_tokens)

    tokens.append("}")
    return tokens


def visit_for_statement(node):
    tokens = []
    id_tokens = []
    from_tokens = []
    to_tokens = []
    statement_tokens = []
    for child in node.children:
        if child.data == "id":
            tokens.append(visit_id(child))
        elif child.data == "expression":
            if id_tokens:
                from_tokens = visit_expression(child)
            else:
                to_tokens = visit_expression(child)
        elif child.data == "statement":
            statement_tokens = visit_statement(child)
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


def visit_while_statement(node):
    tokens = []
    for child in node.children:
        if child.data == "expression":
            tokens.append("while")
            tokens.append("(")
            expression_tokens = visit_expression(child)
            tokens.extend(expression_tokens)
            tokens.append(")")
        elif child.data == "statement":
            tokens.append("{")
            statement_tokens = visit_statement(child)
            tokens.extend(statement_tokens)
            tokens.append("}")
        else:
            raise Exception("Unknown while_statement child data: {}".format(child.data))
    return tokens


def visit_statement(node):
    tokens = []
    for child in node.children:
        if child.data == "procedure_call":
            procedure_call_tokens = visit_procedure_call(child)
            tokens.extend(procedure_call_tokens)
        elif child.data == "compound_statement":
            compound_statement_tokens = visit_compound_statement(child)
            tokens.extend(compound_statement_tokens)
        elif child.data == "if_else_statement":
            if_else_statement_tokens = visit_if_else_statement(child)
            tokens.extend(if_else_statement_tokens)
        elif child.data == "for_statement":
            for_statement_tokens = visit_for_statement(child)
            tokens.extend(for_statement_tokens)
        elif child.data == "while_statement":
            while_statement_tokens = visit_while_statement(child)
            tokens.extend(while_statement_tokens)
        elif child.data == "assign_statement":
            assign_statement_tokens = visit_assign_statement(child)
            tokens.extend(assign_statement_tokens)
        elif child.data == "empty":
            return tokens
        else:
            raise Exception("Unknown statement child data: {}".format(child.data))
        tokens.append(";")
    return tokens


def visit_const_value(node):
    tokens = []
    for child in node.children:
        if isinstance(child, lark.lexer.Token):
            if child.type == "PLUS":
                tokens.append("+")
            elif child.type == "MINUS":
                tokens.append("-")
            elif child.type == "LETTER":
                tokens.append("'" + child.value + "'")
            else:
                raise Exception("Unknown const_value child type: {}".format(child.type))

        elif child.data == "num":
            num_tokens = visit_num(child)
            tokens.extend(num_tokens)
        else:
            raise Exception("Unknown const_value child data: {}".format(child.data))

    return tokens


def visit_const_declaration(node):
    tokens = []
    for child in node.children:
        if child.data == "id":
            tokens.append("const")
            tokens.append("int")
            tokens.append(visit_id(child))
        elif child.data == "const_value":
            tokens.append("=")
            tokens.extend(visit_const_value(child))
            tokens.append(";")
        elif child.data == "const_declaration":
            tokens.extend(visit_const_declaration(child))
        else:
            raise Exception(
                "Unknown const_declaration child data: {}".format(child.data)
            )
    return tokens


def visit_const_declarations(node):
    tokens = []
    for child in node.children:
        if child.data == "const_declaration":
            tokens.extend(visit_const_declaration(child))
        elif child.data == "empty":
            return tokens
        else:
            raise Exception(
                "Unknown const_declarations child data: {}".format(child.data)
            )
    return tokens


def visit_var_declaration(node):
    tokens = []
    idlist = []
    id_type = None
    for child in node.children:
        if child.data == "idlist":
            idlist = visit_idlist(child)
        elif child.data == "type":
            id_type = visit_type(child)
        elif child.data == "var_declaration":
            tokens.extend(visit_var_declaration(child))
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
        tokens.append(";")
    return tokens


def visit_var_declarations(node):
    tokens = []
    for child in node.children:
        if child.data == "var_declaration":
            tokens.extend(visit_var_declaration(child))
        elif child.data == "empty":
            return tokens
        else:
            raise Exception(
                "Unknown var_declarations child data: {}".format(child.data)
            )
    return tokens


def visit_program_head(node):
    # tokens = []
    # for child in node.children:
    #     if child.data == "id":
    #         id_tokens = visit_id(child)
    #         tokens.extend(id_tokens)
    #         tokens.append(";\n")
    #     elif child.data == "idlist":
    #         tokens.append("int ")
    #         idlist_tokens = visit_idlist(child)

    #         tokens.append(";")
    #     else:
    #         raise Exception("Unknown program_head child data: {}".format(child.data))
    tokens = []
    return tokens


def visit_subprogram_body(node):
    tokens = []
    for child in node.children:
        if child.data == "const_declarations":
            tokens.extend(visit_const_declarations(child))
        elif child.data == "var_declarations":
            tokens.extend(visit_var_declarations(child))
        elif child.data == "compound_statement":
            tokens.extend(visit_compound_statement(child))
        else:
            raise Exception("Unknown subprogram_body child data: {}".format(child.data))
    return tokens


def visit_subprogram(node):
    tokens = []
    for child in node.children:
        if child.data == "subprogram_head":
            tokens.extend(visit_subprogram_head(child))
        elif child.data == "subprogram_body":
            tokens.extend(visit_subprogram_body(child))
        else:
            raise Exception("Unknown subprogram child data: {}".format(child.data))
    return tokens


def visit_subprogram_declarations(node):
    tokens = []
    for child in node.children:
        if child.data == "subprogram":
            tokens.extend(visit_subprogram(child))
        elif child.data == "subprogram_declarations":
            tokens.extend(visit_subprogram_declarations(child))
        elif child.data == "empty":
            return tokens
        else:
            raise Exception(
                "Unknown subprogram_declarations child data: {}".format(child.data)
            )
    return tokens


def visit_program_body(node):
    tokens = []
    for child in node.children:
        if child.data == "const_declarations":
            tokens.extend(visit_const_declarations(child))
        elif child.data == "var_declarations":
            tokens.extend(visit_var_declarations(child))
        elif child.data == "subprogram_declarations":
            tokens.extend(visit_subprogram_declarations(child))
        elif child.data == "compound_statement":
            tokens.extend(visit_compound_statement(child))
        else:
            raise Exception("Unknown program_body child data: {}".format(child.data))
    return tokens


def visit_programstruct(node):
    tokens = []
    for child in node.children:
        if child.data == "program_head":
            tokens.extend(visit_program_head(child))
        elif child.data == "program_body":
            tokens.extend(visit_program_body(child))
        else:
            raise Exception("Unknown programstruct child data: {}".format(child.data))
    return tokens
