from lark import Lark

from .context import Context
from .result import Result
from .rules import rules
from .utils import format_code, preprocess, postprocess
from .visitors import visit_programstruct


class Converter:
    def __init__(self):
        self.parser = Lark(rules, start = "programstruct", debug = True)

    def __call__(self, code, debug = False) -> tuple[bool, str]:
        status = True
        parser = self.parser
        code = preprocess(code)
        tree = parser.parse(code)
        context = Context()
        tokens = visit_programstruct(tree, context)
        if context.on_error:
            status = False
        tokens = postprocess(tokens)
        result_string = "\n".join(tokens)
        result_string = format_code(result_string)
        return status, result_string

    def convert(self, code, debug = False) -> Result:
        status = True
        parser = self.parser
        code = preprocess(code)
        try:
            tree = parser.parse(code)
        except Exception as e:
            return Result("", False, [str(e)])
        context = Context()
        tokens = visit_programstruct(tree, context)
        tokens = postprocess(tokens)
        result_string = "\n".join(tokens)
        result_string = format_code(result_string)
        if context.on_error:
            error_messages = context.error_messages
            return Result(result_string, False, error_messages)
        return Result(result_string, True)


def error_handler(e):
    print(e.token.type)
    return False
