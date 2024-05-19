from .utils import code_analyze


class Result:
    """
    Represents the result of a code analysis.

    Attributes:
        code (str): The code that was analyzed.
        success (bool): Indicates whether the analysis was successful or not.
        error_messages (list): A list of error messages, if any.
        error_info (str): Additional information about the error, if any. Detected by Clang.
    """

    def __init__(self, code: str, success: bool = True, error_messages = None):
        if error_messages is None:
            error_messages = []
        if not success and code != "":
            error_info = code_analyze(code)
        else:
            error_info = ""
        self.code = code
        self.success = success
        self.error_messages = error_messages
        self.error_info = error_info
