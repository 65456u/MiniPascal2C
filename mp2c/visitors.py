import lark
from utils import *

"""
statement (Depends on various other non-terminals like id, expression, etc.)
else_part (Depends on statement)
statement_list (Depends on statement)
compound_statement (Depends on statement_list)
subprogram_body (Depends on const_declarations, var_declarations, and compound_statement)
subprogram (Depends on subprogram_head and subprogram_body)
subprogram_declarations (Depends on subprogram)
var_declaration (Depends on idlist and type)
var_declarations (Depends on var_declaration)
const_declaration (Depends on id and const_value)
const_value (Depends on num and other factors)
const_declarations (Depends on const_declaration)
program_body (Depends on various other non-terminals)
program_head (Depends on id and idlist)
programstruct (Depends on program_head, program_body)
"""


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

    return tokens


def visit_period(node):
    periods = []
    current_period = []
    for children in node.children:
        if isinstance(children, lark.lexer.Token):
            current_period.append(int(children.value))
        elif children.data == "period":
            current_period = visit_period(children)
            periods.append(current_period)
            current_period = []
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
    return ids


def visit_value_parameter(node):
    ids = []
    type = None
    for child in node.children:
        if child.data == "idlist":
            ids = visit_idlist(child)
        elif child.data == "basic_type":
            type = visit_basic_type(child)
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
    if basic_type:
        tokens.append(basic_type)
    else:
        tokens.append("void")
    tokens.append(id)
    tokens.extend(formal_parameter)


def visit_func_id(node):
    tokens = []
    for child in node.children:
        tokens = visit_id(child)
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
    return tokens


def visit_variable(node):
    tokens = []
    for child in node.children:
        if child.data == "id":
            tokens.append(visit_id(child))
        elif child.data == "expression":
            tokens.append("[")
            expression_tokens = visit_expression(child)
            tokens.extend(expression_tokens)
            tokens.append("]")
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


def visit_func_id(node):
    tokens = []
    for child in node.children:
        id = visit_id(child)
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
