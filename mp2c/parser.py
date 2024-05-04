from typing import Any
from .visitors import visit_programstruct
from lark import Lark
from .utils import format_code
from .context import Context
from .rules import rules


class MP2CParser:
    def __init__(self):
        self.parser = Lark(rules, start="programstruct")

    def __call__(self, code) -> Any:
        parser = self.parser
        tree = parser.parse(code)
        context = Context()
        tokens = visit_programstruct(tree, context)
        result_string = "\n".join(tokens)
        result_string = format_code(result_string)
        return tree, tokens, result_string
