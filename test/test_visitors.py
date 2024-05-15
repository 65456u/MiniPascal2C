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
        assert result == (['int', 'abc'], {'ids': ['abc'], 'type': 'int'})
