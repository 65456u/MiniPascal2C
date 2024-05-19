from lark import Lark

from .context import Context
from .result import Result
from .rules import rules
from .utils import format_code, preprocess, postprocess
from .visitors import visit_programstruct


class Converter:
    """
    Converts MiniPascal code to C code using a parser.

    Attributes:
        parser (Lark): The parser used for parsing MiniPascal code.

    Methods:
        __init__(self): Initializes the Converter object.
        __call__(self, code, debug=False) -> tuple[bool, str]: Converts the given MiniPascal code to C code.
        convert(self, code) -> Result: Converts the given MiniPascal code to C code and returns the result.
    """

    def __init__(self):
        self.parser = Lark(rules, start = "programstruct")

    def __call__(self, code, debug = False) -> tuple[bool, str]:
        """
        Converts the given MiniPascal code to C code.

        Args:
            code (str): The MiniPascal code to be converted.
            debug (bool, optional): Whether to enable debug mode. Defaults to False.

        Returns:
            tuple[bool, str]: A tuple containing the conversion status (True if successful, False otherwise)
            and the converted C code as a string.
        """
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

    def convert(self, code) -> Result:
        """
        Converts the given MiniPascal code to C code and returns the result.

        Args:
            code (str): The MiniPascal code to be converted.

        Returns:
            Result: The conversion result, which includes the converted C code as a string and error messages.
        """
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
