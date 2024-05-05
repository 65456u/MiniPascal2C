from typing import Any

from lark import Lark

from .context import Context
from .rules import rules
from .utils import format_code, preprocess, postprocess
from .visitors import visit_programstruct


class Converter:
    def __init__(self):
        self.parser = Lark(rules, start="programstruct")

    def __call__(self, code) -> Any:
        parser = self.parser
        code = preprocess(code)
        tree = parser.parse(code)
        context = Context()
        tokens = visit_programstruct(tree, context)
        tokens = postprocess(tokens)
        result_string = "\n".join(tokens)
        result_string = format_code(result_string)
        return tree, tokens, result_string
