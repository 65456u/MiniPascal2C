from .utils import code_analyze


class Result:
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
