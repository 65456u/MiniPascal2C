from lark.lark import Token

from .context import FunctionSymbol
from .utils import *


def visit_empty(node: Tree, context: Context):
    """
    This function is used to visit an empty node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: An empty list of tokens.
    """
    tokens = []
    return tokens


def visit_optional_fraction(node: Tree, context: Context):
    """
    This function is used to visit an optional fraction node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        str: The value of the first child of the node.
    """
    return node.children[0].value


def visit_num(node: Tree, context: Context):
    """
    This function is used to visit a number node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list containing the tokens and the type name.
    """
    tokens = []
    typename = ""
    for child in node.children:
        if isinstance(child, Token):
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


def visit_period(node: Tree, context: Context):
    """
    Visit a period node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of periods.
    """
    periods = []
    current_period = []
    for child in node.children:
        if isinstance(child, Token):
            current_period.append(int(child.value))
        elif child.data == "period":
            current_period = visit_period(child, context)
            periods.extend(current_period)
            current_period = []
        else:
            raise Exception("Unknown period child data: {}".format(child.data))
    periods.append(current_period)
    return periods


def visit_basic_type(node: Tree, context: Context):
    """
    Visit a basic type node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        str: The basic type of the node.
    """
    return type_map[node.children[0].value]


def visit_type(node: Tree, context: Context):
    """
    Visit a type node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        dict: A dictionary containing the basic type, whether it's an array, and the period.
    """
    type_ = {"basic_type": None, "is_array": False, "period": []}
    for child in node.children:
        if child.data == "basic_type":
            type_["basic_type"] = visit_basic_type(child, context)
        elif child.data == "period":
            type_["period"] = visit_period(child, context)
            type_["is_array"] = True
        else:
            raise Exception("Unknown type child data: {}".format(child.data))
    return type_


def visit_id(node: Tree, context: Context, func_name: str):
    """
    Visit an id node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        str: The id of the node.
    """
    name = node.children[0].value
    if name == func_name:
        return "_" + name
    else:
        return node.children[0].value


def visit_idlist(node: Tree, context: Context):
    """
    Visit an idlist node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of ids.
    """
    ids = []
    for child in node.children:
        if child.data == "id":
            # 从idlist得到的id不需要考虑func_name修正
            ids.append(visit_id(child, context, ""))
        elif child.data == "idlist":
            ids.extend(visit_idlist(child, context))
        else:
            raise Exception("Unknown idlist child data: {}".format(child.data))
    return ids


def visit_value_parameter(node: Tree, context: Context):
    """
    Visit a value parameter node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        dict: A dictionary containing the ids and type of the node.
    """
    ids = []
    type_ = None
    for child in node.children:
        if child.data == "idlist":
            ids = visit_idlist(child, context)
        elif child.data == "basic_type":
            type_ = visit_basic_type(child, context)
        else:
            raise Exception("Unknown value_parameter child data: {}".format(child.data))
    return {"ids": ids, "type": type_}


def visit_var_parameter(node: Tree, context: Context):
    """
    Visit a var parameter node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        tuple: A tuple containing the tokens and value parameter.
    """
    value_parameter = visit_value_parameter(node.children[0], context)
    tokens = construct_parameter_tokens(value_parameter, context, var = True)

    return tokens, value_parameter


def construct_parameter_tokens(value_parameter, context, var = False):
    """
    Construct parameter tokens.

    Args:
        value_parameter (dict): The value parameter.
        context (Context): The context in which the node exists.
        var (bool, optional): A flag indicating if the parameter is a variable. Defaults to False.

    Returns:
        list: A list of tokens.
    """
    tokens = []
    first = True
    for id_ in value_parameter["ids"]:
        if first:
            first = False
        else:
            tokens.append(",")
        id_type = value_parameter["type"]
        context.register_value(id_, id_type, True, var = var)
        tokens.append(id_type)
        if var:
            tokens.append("*")
        tokens.append(id_)
    return tokens


def visit_parameter(node: Tree, context: Context):
    """
    Visit a parameter node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        tuple: A tuple containing the tokens, parameter, and a flag indicating if it's a variable.
    """
    tokens = []
    parameter = None
    var = False
    for child in node.children:
        if child.data == "var_parameter":
            tokens, parameter = visit_var_parameter(child, context)
            var = True
        elif child.data == "value_parameter":
            parameter = visit_value_parameter(child, context)
            tokens = construct_parameter_tokens(parameter, context)
        else:
            raise Exception("Unknown parameter child data: {}".format(child.data))
    return tokens, parameter, var


def visit_parameter_list(node: Tree, context: Context):
    """
    Visit a parameter list node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        tuple: A tuple containing the tokens, parameter list, and a list of flags indicating if they are variables.
    """
    tokens = []
    first = True
    parameter_list = []
    is_var = []
    for child in node.children:
        if child.data == "empty":
            return tokens, parameter_list, is_var
        assert child.data == "parameter"
        if first:
            first = False
        else:
            tokens.append(",")
        parameter_tokens, parameter, var = visit_parameter(child, context)
        tokens.extend(parameter_tokens)
        parameter_list.append(parameter)
        is_var.append(var)
    return tokens, parameter_list, is_var


def visit_formal_parameter(node: Tree, context: Context):
    """
    Visit a formal parameter node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        tuple: A tuple containing the tokens, parameter list, and a list of flags indicating if they are variables.
    """
    tokens = ["("]
    parameter_list_tokens, parameter_list, var_list = visit_parameter_list(node.children[0], context)
    tokens.extend(parameter_list_tokens)
    tokens.append(")")
    return tokens, parameter_list, var_list


def visit_func_id(node):
    """
    Visit a function id node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.

    Returns:
        list: A list of tokens representing the function id.
    """
    tokens = []
    for child in node.children:
        assert child.data == "id"
        for grandchild in child.children:
            if grandchild.type == "IDENTIFIER_TOKEN":
                tokens.append(grandchild.value)
            else:
                raise Exception("Unknown func_id grandchild type: {}".format(grandchild.type))
    return tokens


def visit_id_varpart(node: Tree, context: Context, func_name: str, id_token):
    """
    Visit an id varpart node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.
        id_token (str): The id token.

    Returns:
        list: A list of tokens representing the id varpart.
    """
    tokens = []
    for child in node.children:
        if child.data == "empty":
            return tokens
        elif child.data == "expression_list":
            tokens.append("[")
            expression_list, expression_types = visit_expression_list(child, context, func_name)
            # check if all elements in expression_types are the integer type
            for expression_type in expression_types:
                if expression_type != "int":
                    # raise Exception("Array index must be integer")
                    error_message = "Array index must be integer, but got {}".format(expression_type)
                    context.record_error(error_message)
            array_symbol = context.get_array(id_token)
            # split expression_list by ','
            count = 0
            for expression_token in expression_list:
                if expression_token == ",":
                    offset = array_symbol.dimensions[count][1]
                    tokens.extend(['-', str(offset)])
                    count += 1
                    tokens.extend(["]", "["])
                else:
                    tokens.append(expression_token)
            offset = array_symbol.dimensions[count][1]
            tokens.extend(['-', str(offset)])
            count += 1
            tokens.append("]")
        else:
            raise Exception("Unknown id_varpart child data: {}".format(child.data))
    return tokens


def visit_variable(node: Tree, context: Context, func_name: str):
    """
    Visit a variable node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        tuple: A tuple containing a list of tokens representing the variable and the variable type.
    """
    tokens = []
    isArray = False
    id_varpart = []
    id_token = None
    var = False
    for child in node.children:
        if child.data == "id":
            id_token = visit_id(child, context, func_name)
        elif child.data == "id_varpart":
            id_varpart = visit_id_varpart(child, context, func_name, id_token)
            if len(id_varpart) > 0:
                isArray = True
        else:
            raise Exception("Unknown variable child data: {}".format(child.data))
    if isArray:
        array = context.get_array(id_token)
        if array is None:
            # raise Exception("Array not declared: {}".format(id_token))
            error_message = "Array used but not declared: {}".format(id_token)
            context.record_error(error_message)
        variable_type = array.type
    else:
        value = context.get_value(id_token)
        if value is None:
            # raise Exception("Variable not declared: {}".format(id_token))
            error_message = "Variable not declared: {}".format(id_token)
            context.record_error(error_message)
            variable_type = ""
        else:
            variable_type = value.type
            var = value.var
    if var:
        tokens.append("*")
    tokens.append(id_token)
    tokens.extend(id_varpart)
    return tokens, variable_type


def visit_variable_list(node: Tree, context: Context, func_name: str):
    """
    Visit a variable list node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the variable list.
    """
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


def visit_expression_list_for_call(node: Tree, context: Context, func_name: str, function_to_call: FunctionSymbol):
    """
    Visit an expression list for a function call in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.
        function_to_call (FunctionSymbol): The function to be called.

    Returns:
        list: A list of tokens representing the expression list for the function call.
    """
    tokens = []
    first = True
    count = 0
    parameter_list = []
    for id_group in function_to_call.parameter_list:
        for _ in id_group["ids"]:
            parameter_list.append(id_group["type"])
    for child in node.children:
        if first:
            first = False
        else:
            tokens.append(",")
        if function_to_call.var_parameter[count]:
            tokens.append("&")
        expression_tokens, expression_type = visit_expression(child, context, func_name)
        try:
            if expression_type != parameter_list[count]:
                # raise Exception("Parameter types do not match")
                error_message = "Parameter types do not match: expected {}, got {}".format(
                    function_to_call.parameter_list[count], expression_type)
                context.record_error(error_message)
        except Exception as e:
            error_message = str(e)
            context.record_error(error_message)
        tokens.extend(expression_tokens)
        count += 1
    if count != len(function_to_call.var_parameter):
        # raise Exception("Number of parameters does not match")
        error_message = "Number of parameters does not match: expected {}, got {}".format(
            len(function_to_call.var_parameter), count)
        context.record_error(error_message)
    return tokens


def visit_function_call(node: Tree, context: Context, func_name: str):
    """
    Visit a function call node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        tuple: A tuple containing a list of tokens representing the function call and the function type.
    """
    tokens = []
    function_type = None
    function = None
    function_name = None
    for child in node.children:
        if child.data == "func_id":
            function_token = visit_func_id(child)
            function_name = function_token[0]
            function = context.get_func(function_name)
            if function is None:
                error_message = "Function not declared: {}".format(function_name)
                context.record_error(error_message)
                function_type = ""
            else:
                function_type = function.header[0]
            tokens.extend(function_token)
            tokens.append("(")
        elif child.data == "expression_list":
            expression_list_tokens = visit_expression_list_for_call(child, context, func_name,
                                                                    function)
            tokens.extend(expression_list_tokens)
        else:
            raise Exception("Unknown procedure_call child data: {}".format(child.data))
    tokens.append(")")
    return tokens, function_type


def visit_factor(node: Tree, context: Context, func_name: str):
    """
    Visit a factor node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        tuple: A tuple containing a list of tokens representing the factor and the factor type.
    """
    tokens = []
    factor_type = None
    for child in node.children:
        if isinstance(child, Token):
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


def visit_term(node: Tree, context: Context, func_name: str):
    """
    Visit a term node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        tuple: A tuple containing a list of tokens representing the term and the term type.
    """
    term_type = None
    tokens = []
    operator = None
    for child in node.children:
        if isinstance(child, Token):
            tokens.append(mulop_map[child.value])
            operator = child.value
            if operator == "/":
                tokens[:0] = ["(", "float", ")"]
        elif child.data == "factor":
            factor_token, factor_type = visit_factor(child, context, func_name)
            tokens.extend(factor_token)
            term_type = factor_type
        elif child.data == "term":
            term_token, term_type = visit_term(child, context, func_name)
            tokens.extend(term_token)
        else:
            raise Exception("Unknown term child data: {}".format(child.data))
        if operator == "/":
            term_type = "float"
    return tokens, term_type


def visit_simple_expression(node: Tree, context: Context, func_name: str):
    """
    Visit a simple expression node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        tuple: A tuple containing a list of tokens representing the simple expression and the simple expression type.
    """
    tokens = []
    simple_expression_type = None
    for child in node.children:
        if isinstance(child, Token):
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


def visit_expression(node: Tree, context: Context, func_name: str):
    """
    Visit an expression node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        tuple: A tuple containing a list of tokens representing the expression and the expression type.
    """
    tokens = []
    isBool = False
    simple_expression_type = None
    for child in node.children:
        if isinstance(child, Token):
            tokens.append(relop_map[child.value])
            isBool = True
        elif child.data == "simple_expression":
            simple_expression_token, simple_expression_type = visit_simple_expression(child, context, func_name)
            tokens.extend(simple_expression_token)
        elif child.data == "char_literal":
            tokens.append(child.children[0].value)
            simple_expression_type = "char"
        elif child.data == "string_literal":
            tokens.append(child.children[0].value)
            simple_expression_type = "char*"
        else:
            raise Exception("Unknown expression child data: {}".format(child.data))
    if isBool:
        expression_type = "bool"
    else:
        expression_type = simple_expression_type
    return tokens, expression_type


def visit_expression_list(node: Tree, context: Context, func_name: str, is_call = False):
    """
    Visit an expression list node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.
        is_call (bool, optional): A flag indicating if the expression list is for a function call. Defaults to False.

    Returns:
        tuple: A tuple containing a list of tokens representing the expression list and a list of expression types.
    """
    tokens = []
    first = True
    expression_types = []
    for child in node.children:
        if first:
            first = False
        else:
            tokens.append(",")
        expression_tokens, expression_type = visit_expression(child, context, func_name)
        expression_types.append(expression_type)
        tokens.extend(expression_tokens)
    return tokens, expression_types


def visit_assign_statement(node: Tree, context: Context, func_name: str):
    """
    Visit an assign statement node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the assign statement.
    """
    tokens = []
    variable_type = None
    expression_type = None
    variable_tokens = []
    expression_tokens = []
    for child in node.children:
        if isinstance(child, Token):
            tokens.append(assignop_map[child.value])
        elif child.data == "expression":
            expression_tokens, expression_type = visit_expression(child, context, func_name)
            tokens.extend(expression_tokens)
        elif child.data == "variable":
            variable_tokens, variable_type = visit_variable(child, context, func_name)
            tokens.extend(variable_tokens)
        else:
            raise Exception(
                "Unknown assignment_statement child data: {}".format(child.data)
            )
    if variable_type != expression_type:
        error_message = "Type mismatch in assignment: {},{} != {}, {}".format(
            "".join(variable_tokens), variable_type, "".join(expression_tokens), expression_type
        )
        context.record_error(error_message)

    return tokens


def visit_if_else_statement(node: Tree, context: Context, func_name: str):
    """
    Visit an if-else statement node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the if-else statement.
    """
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


def visit_else_part(node: Tree, context: Context, func_name: str):
    """
    Visit an else part node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the else part.
    """
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


def construct_read_params(node: Tree, context: Context, func_name: str):
    """
    Construct read parameters from a node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the read parameters.
    """
    tokens = []
    types = []
    expressions = []
    for child in node.children:
        if child.data == "expression":
            expression_tokens, expression_type = visit_expression(child, context, func_name)
            expressions.append(expression_tokens)
            types.append(expression_type)
        else:
            raise Exception("Unknown read_params child data: {}".format(child.data))
    format_ = types_to_format(types, context)
    tokens.append(format_)
    for expression in expressions:
        tokens.append(",")
        tokens.append("&")
        tokens.extend(expression)
    return tokens


def types_to_format(types, context, line = False):
    """
    Convert types to format strings.

    Args:
        types (list): A list of types.
        context (Context): The context in which the node exists.
        line (bool, optional): A flag indicating if a newline should be added. Defaults to False.

    Returns:
        str: The format string.
    """
    format_ = '"'
    for id_type in types:
        if id_type == "int":
            format_ += r"%d"
        elif id_type == "float":
            format_ += r"%f"
        elif id_type == "char":
            format_ += r"%c"
        elif id_type == "":
            error_message = "Variable not declared"
            context.record_error(error_message)
        elif id_type == "char*":
            format_ += r"%s"
        else:
            raise Exception("Unknown type: {}".format(id_type))
    if line:
        format_ += r"\n"
    format_ += '"'
    return format_


def construct_write_params(node: Tree, context: Context, func_name: str, line = False):
    """
    Construct write parameters from a node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.
        line (bool, optional): A flag indicating if a newline should be added. Defaults to False.

    Returns:
        list: A list of tokens representing the write parameters.
    """
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
    format_ = types_to_format(types, context, line)
    tokens.append(format_)
    for expression in expressions:
        tokens.append(",")
        tokens.extend(expression)
    if len(tokens) == 0:
        tokens.append('""')
    return tokens


def visit_procedure_call(node: Tree, context: Context, func_name: str):
    """
    Visit a procedure call node in the parse tree.

    This function handles the procedure calls in the code, including built-in procedures like 'read', 'write', and 'writeln'.
    It also handles user-defined procedures.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the procedure call.
    """
    tokens = []
    isRead = False
    isWrite = False
    isWriteLn = False
    procedure_name = None
    flag = False
    for child in node.children:
        if child.data == "id":
            if child.children[0].value == "read":
                isRead = True
                tokens.append("scanf")
            elif child.children[0].value == "write":
                isWrite = True
                tokens.append("printf")
            elif child.children[0].value == "writeln":
                isWriteLn = True
                tokens.append("printf")
            else:
                # 过程调用不进行func_name修正
                procedure_name = visit_id(child, context, "")
                tokens.append(procedure_name)
        elif child.data == "expression_list":
            flag = True
            tokens.append("(")
            if isRead:
                expression_list_tokens = construct_read_params(
                    child, context, func_name
                )
            elif isWrite:
                expression_list_tokens = construct_write_params(
                    child, context, func_name
                )
            elif isWriteLn:
                expression_list_tokens = construct_write_params(
                    child, context, func_name, True
                )
            else:
                expression_list_tokens = visit_expression_list_for_call(
                    child, context, func_name, context.get_func(procedure_name)
                )

            tokens.extend(expression_list_tokens)
            tokens.append(")")
        else:
            raise Exception("Unknown procedure_call child data: {}".format(child.data))
    if not flag:
        tokens.append("(")
        if isWriteLn:
            tokens.append(r'"\n"')
        elif isWrite:
            tokens.append('""')
        tokens.append(")")
    return tokens


def visit_statement_list(node: Tree, context: Context, func_name: str):
    """
    Visit a statement list node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the statement list.
    """
    tokens = []
    for child in node.children:
        if child.data == "statement":
            statement_tokens = visit_statement(child, context, func_name)
            tokens.extend(statement_tokens)
        elif child.data == "statement_list":
            statement_list_tokens = visit_statement_list(child, context, func_name)
            tokens.extend(statement_list_tokens)
        else:
            raise Exception("Unknown statement_list child data: {}".format(child.data))
    return tokens


def visit_compound_statement(node: Tree, context: Context, func_name: str):
    """
    Visit a compound statement node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the compound statement.
    """
    tokens = []
    assert node.children[0].data == "statement_list"
    statement_list_tokens = visit_statement_list(node.children[0], context, func_name)
    tokens.extend(statement_list_tokens)
    return tokens


def visit_for_statement(node: Tree, context: Context, func_name: str):
    """
    Visit a for statement node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the for statement.
    """
    tokens = []
    id_token = []
    from_tokens = []
    to_tokens = []
    statement_tokens = []
    down_to = False
    first = True
    for child in node.children:
        if isinstance(child, Token):
            if child.type == "DOWN":
                down_to = True
            elif child.type != "ASSIGNOP":
                raise Exception("Unknown for_statement child type: {}".format(child.type))
        elif child.data == "id":
            context.enter_scope()
            id_token = visit_id(child, context, func_name)
            context.register_value(id_token, "int", True)
        elif child.data == "expression":
            if first:
                from_tokens, from_type = visit_expression(child, context, func_name)
                first = False
            else:
                to_tokens, to_type = visit_expression(child, context, func_name)
        elif child.data == "statement":
            statement_tokens = visit_statement(child, context, func_name)
        else:
            raise Exception("Unknown for_statement child data: {}".format(child.data))
    tokens.extend(["for", "("])
    tokens.extend(id_token)
    tokens.append("=")
    tokens.extend(from_tokens)
    tokens.append(";")
    tokens.extend(id_token)
    tokens.append("<=")
    tokens.extend(to_tokens)
    tokens.append(";")
    tokens.extend(id_token)
    if down_to:
        tokens.append("--")
    else:
        tokens.append("++")
    tokens.append(")")
    tokens.append("{")
    tokens.extend(statement_tokens)
    tokens.append("}")
    context.exit_scope()
    return tokens


def visit_while_statement(node: Tree, context: Context, func_name: str):
    """
    Visit a while statement node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the while statement.
    """
    tokens = []
    for child in node.children:
        if child.data == "expression":
            tokens.append("while")
            tokens.append("(")
            expression_tokens, expression_type = visit_expression(child, context, func_name)
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


def visit_statement(node: Tree, context: Context, func_name: str):
    """
    Visit a statement node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.

    Returns:
        list: A list of tokens representing the statement.
    """
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


def visit_const_value(node: Tree, context: Context):
    """
    Visit a constant value node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list containing tokens representing the constant value and its type.
    """
    tokens = []
    typename = ""
    for child in node.children:
        if isinstance(child, Token):
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


def visit_const_declaration(node: Tree, context: Context):
    """
    Visit a constant declaration node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the constant declaration.
    """
    tokens = []
    const_id = ""
    for child in node.children:
        if child.data == "id":
            tokens.append("const")
            const_id = visit_id(child, context, "")
        elif child.data == "const_value":
            res = visit_const_value(child, context)
            tokens.append(res[1])
            tokens.append(const_id)
            tokens.append("=")
            tokens.extend(res[0])
            tokens.append(";")
            context.register_value(const_id, res[1], False, res[0])
        elif child.data == "const_declaration":
            tokens.extend(visit_const_declaration(child, context))
        else:
            raise Exception("Unknown const_declaration child data: {}".format(child.data))
    return tokens


def visit_const_declarations(node: Tree, context: Context):
    """
    Visit a constant declarations node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the constant declarations.
    """
    tokens = []
    for child in node.children:
        if child.data == "const_declaration":
            tokens.extend(visit_const_declaration(child, context))
        elif child.data == "empty":
            return tokens
        else:
            raise Exception("Unknown const_declarations child data: {}".format(child.data))
    return tokens


def visit_var_declaration(node: Tree, context: Context):
    """
    Visit a variable declaration node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the variable declaration.
    """
    tokens = []
    id_lists = []
    id_types = []
    for child in node.children:
        if child.data == "idlist":
            id_lists.append(visit_idlist(child, context))
        elif child.data == "type":
            id_types.append(visit_type(child, context))
        elif child.data == "var_declaration":
            tokens.extend(visit_var_declaration(child, context))
        else:
            raise Exception("Unknown var_declaration child data: {}".format(child.data))
    for id_list, id_type in zip(id_lists, id_types):
        for id_ in id_list:
            tokens.append(id_type["basic_type"])
            tokens.append(id_)
            if id_type["is_array"]:
                for period in id_type["period"]:
                    tokens.append("[")
                    tokens.append(str(period[1] - period[0] + 1))
                    tokens.append("]")
                context.register_array(id_, id_type["basic_type"], id_type["period"])
            else:
                context.register_value(id_, id_type["basic_type"], True)
            tokens.append(";")
    return tokens


def visit_var_declarations(node: Tree, context: Context):
    """
    Visit a variable declarations node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the variable declarations.
    """
    tokens = []
    for child in node.children:
        if child.data == "var_declaration":
            tokens.extend(visit_var_declaration(child, context))
        elif child.data == "empty":
            return tokens
        else:
            raise Exception("Unknown var_declarations child data: {}".format(child.data))
    return tokens


def visit_program_head(node: Tree, context: Context):
    """
    Visit a program head node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the program head.
    """
    tokens = ['#include <stdio.h>', '#include <math.h>']
    return tokens


def visit_subprogram_body(node: Tree, context: Context, func_name: str, ret_type: str):
    """
    Visit a subprogram body node in the parse tree.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.
        func_name (str): The name of the function.
        ret_type (str): The return type of the function.

    Returns:
        list: A list of tokens representing the subprogram body.
    """
    if ret_type != "void":
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


def visit_function_declaration(child, context):
    """
    Visit a function declaration node in the parse tree.

    Args:
        child (Tree): The child node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the function declaration.
    """
    head_tokens = []
    function_name = ""
    formal_parameter_tokens = []
    parameter_info_list = []
    var_list = []
    basic_type = None
    body_tokens = ["{"]
    subprogram_body_tokens = []
    for child in child.children:
        if child.data == "id":
            function_name = visit_id(child, context, "")
        elif child.data == "formal_parameter":
            formal_parameter_tokens, parameter_info_list, is_vars = visit_formal_parameter(child, context)
            for id_group, var in zip(parameter_info_list, is_vars):
                for _ in id_group["ids"]:
                    var_list.append(var)
        elif child.data == "basic_type":
            basic_type = visit_basic_type(child, context)
        elif child.data == "subprogram_body":
            head_tokens.append(basic_type)
            head_tokens.append(function_name)
            head_tokens.extend(formal_parameter_tokens)
            context.register_func(function_name, head_tokens, parameter_info_list, var_list, body_tokens)
            context.enter_scope()
            subprogram_body_tokens = visit_subprogram_body(child, context, function_name, basic_type)
            context.exit_scope()
        else:
            raise Exception("Unknown function_declaration child data: {}".format(child.data))
    body_tokens.append(basic_type)
    body_tokens.append("_" + function_name)
    body_tokens.append(";")
    body_tokens.extend(subprogram_body_tokens)
    body_tokens.append("return")
    body_tokens.append("_" + function_name)
    body_tokens.append(";")
    body_tokens.append("}")
    context.register_func(function_name, head_tokens, parameter_info_list, var_list, body_tokens)
    return head_tokens


def visit_procedure_declaration(child, context):
    """
    Visit a procedure declaration node in the parse tree.

    This function handles the declaration of a procedure in the parse tree. It extracts the procedure name,
    formal parameters, and body of the procedure. It also registers the procedure in the context.

    Args:
        child (Tree): The child node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the procedure declaration.
    """
    head_tokens = []
    procedure_name = ""
    formal_parameter_tokens = []
    parameter_info_list = []
    body_tokens = ["{"]
    subprogram_body_tokens = []
    var_list = []
    for child in child.children:
        if child.data == "id":
            procedure_name = visit_id(child, context, "")
        elif child.data == "formal_parameter":
            formal_parameter_tokens, parameter_info_list, var_s = visit_formal_parameter(child, context)
            for id_group, var in zip(parameter_info_list, var_s):
                for _ in id_group["ids"]:
                    var_list.append(var)
        elif child.data == "subprogram_body":
            head_tokens.append("void")
            head_tokens.append(procedure_name)
            head_tokens.extend(formal_parameter_tokens)
            context.register_func(procedure_name, head_tokens, parameter_info_list, var_list, body_tokens)
            context.enter_scope()
            subprogram_body_tokens = visit_subprogram_body(child, context, procedure_name, "void")
            context.exit_scope()
        else:
            raise Exception("Unknown procedure_declaration child data: {}".format(child.data))
    body_tokens.extend(subprogram_body_tokens)
    body_tokens.append("}")
    context.register_func(procedure_name, head_tokens, parameter_info_list, var_list, body_tokens)
    return head_tokens


def visit_subprogram(node: Tree, context: Context):
    """
    Visit a subprogram node in the parse tree.

    This function handles the subprogram node in the parse tree. It checks if the subprogram is a function or a procedure
    and calls the appropriate function to handle it.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the subprogram.
    """
    tokens = []
    for child in node.children:
        if child.data == "function_declaration":
            function_declaration_tokens = visit_function_declaration(child, context)
            tokens.extend(function_declaration_tokens)
        elif child.data == "procedure_declaration":
            procedure_declaration_tokens = visit_procedure_declaration(child, context)
            tokens.extend(procedure_declaration_tokens)
        else:
            raise Exception("Unknown subprogram child data: {}".format(child.data))
    tokens.append(";")
    return []


def visit_subprogram_declarations(node: Tree, context: Context):
    """
    Visit a subprogram declarations node in the parse tree.

    This function handles the subprogram declarations node in the parse tree. It iterates over the children of the node
    and calls the function to handle subprogram nodes.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the subprogram declarations.
    """
    tokens = []
    for child in node.children:
        if child.data == "subprogram":
            tokens.extend(visit_subprogram(child, context))
        elif child.data == "empty":
            return tokens
        elif child.data == "subprogram_declarations":
            tokens.extend(visit_subprogram_declarations(child, context))
        else:
            raise Exception(
                "Unknown subprogram_declarations child data: {}".format(child.data)
            )
    return tokens


def visit_program_body(node: Tree, context: Context):
    """
    Visit a program body node in the parse tree.

    This function handles the program body node in the parse tree. It iterates over the children of the node
    and calls the appropriate function to handle each child node.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the program body.
    """
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


def visit_programstruct(node: Tree, context: Context):
    """
    Visit a program structure node in the parse tree.

    This function handles the program structure node in the parse tree. It iterates over the children of the node
    and calls the appropriate function to handle each child node. It also handles the declaration of library functions
    and the registration of functions in the context.

    Args:
        node (Tree): The node in the parse tree.
        context (Context): The context in which the node exists.

    Returns:
        list: A list of tokens representing the program structure.
    """
    context.enter_scope()
    tokens = []
    program_head_tokens = []
    program_body_tokens = []
    context.declare_library_functions()
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
        if functions[function].is_library:
            continue
        tokens.extend(functions[function].header)
        tokens.append(";")
    tokens.extend(program_body_tokens)
    for function in functions:
        if functions[function].is_library:
            continue
        tokens.extend(functions[function].header)
        tokens.extend(functions[function].tokens)
    context.exit_scope()
    return tokens
