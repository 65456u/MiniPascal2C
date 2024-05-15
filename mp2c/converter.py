from lark import Lark

from .context import Context
from .rules import rules
from .utils import format_code, preprocess, postprocess
from .visitors import visit_programstruct


class Converter:
    def __init__(self):
        self.parser = Lark(rules, start = "programstruct", debug = True)

    def __call__(self, code, debug = False) -> tuple[bool, str]:
        if not debug:
            parser = self.parser
            try:
                code = preprocess(code)
            except Exception as e:
                return False, "Preprocess Error: " + str(e)
            try:
                tree = parser.parse(code)
            except Exception as e:
                return False, "Parsing Error: " + str(e)
            context = Context()
            try:
                tokens = visit_programstruct(tree, context)
            except Exception as e:
                return False, "Visiting Error: " + str(e)
            try:
                tokens = postprocess(tokens)
            except Exception as e:
                return False, "Postprocess Error: " + str(e)
            result_string = "\n".join(tokens)
            result_string = format_code(result_string)
            return True, result_string
        else:
            parser = self.parser
            code = preprocess(code)
            tree = parser.parse(code)
            context = Context()
            tokens = visit_programstruct(tree, context)
            tokens = postprocess(tokens)
            result_string = "\n".join(tokens)
            result_string = format_code(result_string)
            return True, result_string


def error_handler(e):
    print(e.token.type)
    return False
