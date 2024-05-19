from lark import Lark

from mp2c import rules
from mp2c.visitors import *


class TestVisitors:
    def test_visit_id(self):
        parser = Lark(rules, start = "id", debug = True)
        context = Context()
        tree = parser.parse("abc")
        result = visit_id(tree, context, "")
        assert result == "abc"

    def test_visit_id_func(self):
        parser = Lark(rules, start = "id", debug = True)
        context = Context()
        tree = parser.parse("abc")
        result = visit_id(tree, context, "abc")
        assert result == "_abc"

    def test_visit_idlist(self):
        parser = Lark(rules, start = "idlist", debug = True)
        context = Context()
        tree = parser.parse("abc,def")
        result = visit_idlist(tree, context)
        assert result == ['abc', 'def']

    def test_visit_type(self):
        parser = Lark(rules, start = "type", debug = True)
        context = Context()
        tree = parser.parse("integer")
        result = visit_type(tree, context)
        type_ = {
            "basic_type": "int",
            "is_array": False,
            "period": [],
        }
        assert type_["basic_type"] == result["basic_type"]
        assert type_["is_array"] == result["is_array"]
        assert type_["period"] == result["period"]

    def test_visit_period(self):
        parser = Lark(rules, start = "period", debug = True)
        context = Context()
        tree = parser.parse("1..10")
        result = visit_period(tree, context)
        assert result == [[1, 10]]

    def test_visit_empty(self):
        parser = Lark(rules, start = "empty", debug = True)
        context = Context()
        tree = parser.parse("")
        result = visit_empty(tree, context)
        assert result == []

    def test_visit_optional_fraction(self):
        parser = Lark(rules, start = "optional_fraction", debug = True)
        context = Context()
        tree = parser.parse(".1")
        result = visit_optional_fraction(tree, context)
        assert result == "1"

    def test_visit_num_integer(self):
        parser = Lark(rules, start = "num", debug = True)
        context = Context()
        tree = parser.parse("1")
        result = visit_num(tree, context)
        assert result == [['1'], "int"]

    def test_visit_num_real(self):
        parser = Lark(rules, start = "num", debug = True)
        context = Context()
        tree = parser.parse("1.1")
        result = visit_num(tree, context)
        assert result == [['1.1'], "float"]

    def test_visit_value_parameter(self):
        parser = Lark(rules, start = "value_parameter", debug = True)
        context = Context()
        tree = parser.parse("abc: integer")
        result = visit_value_parameter(tree, context)
        assert result == {'ids': ['abc'], 'type': 'int'}

    def test_visit_var_parameter(self):
        parser = Lark(rules, start = "var_parameter", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("var abc: integer")
        result = visit_var_parameter(tree, context)
        assert result == (['int', '*', 'abc'], {'ids': ['abc'], 'type': 'int'})

    def test_visit_parameter(self):
        parser = Lark(rules, start = "parameter", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("var abc: integer")
        result = visit_parameter(tree, context)
        assert result == (['int', '*', 'abc'], {'ids': ['abc'], 'type': 'int'}, True)

    def test_visit_parameter_list(self):
        parser = Lark(rules, start = "parameter_list", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("var abc: integer")
        result = visit_parameter_list(tree, context)
        assert result == (['int', '*', 'abc'], [{'ids': ['abc'], 'type': 'int'}], [True])

    def test_formal_parameter(self):
        parser = Lark(rules, start = "formal_parameter", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("(var abc: integer)")
        result = visit_formal_parameter(tree, context)
        assert result == (['(', 'int', '*', 'abc', ')'], [{'ids': ['abc'], 'type': 'int'}], [True])

    def test_variable(self):
        parser = Lark(rules, start = "variable", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("abc")
        result = visit_variable(tree, context, "")
        assert result == (['abc'], '')

    def test_variable_list(self):
        parser = Lark(rules, start = "variable_list", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("abc,def")
        result = visit_variable_list(tree, context, "")
        assert result == ['abc', ',', 'def']

    def test_func_id(self):
        parser = Lark(rules, start = "func_id", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("abc")
        result = visit_func_id(tree)
        assert result == ['abc']

    def test_factor_num(self):
        parser = Lark(rules, start = "factor", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("1")
        result = visit_factor(tree, context, "")
        assert result == (['1'], 'int')

    def test_factor_variable(self):
        parser = Lark(rules, start = "factor", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("abc")
        result = visit_factor(tree, context, "")
        assert result == (['abc'], '')

    def test_factor_function_call(self):
        parser = Lark(rules, start = "factor", debug = True)
        context = Context()
        context.enter_scope()
        context.declare_library_functions()
        tree = parser.parse("cos(1)")
        result = visit_factor(tree, context, "")
        assert result == (['cos', '(', '1', ')'], 'float')

    def test_term_div(self):
        parser = Lark(rules, start = "term", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("1 / 2")
        result = visit_term(tree, context, "")
        assert result == (['(', 'float', ')', '1', '/', '2'], 'float')

    def test_term_mul(self):
        parser = Lark(rules, start = "term", debug = True)
        context = Context()
        context.enter_scope()
        tree = parser.parse("1 * 2")
        result = visit_term(tree, context, "")
        assert result == (['1', '*', '2'], 'int')
