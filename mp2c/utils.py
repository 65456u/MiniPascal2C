import re
import subprocess
import tempfile
from enum import Enum

from lark.lark import Tree

from .context import Context

type_map = {"integer": "int", "real": "float", "boolean": "bool", "char": "char", "string": "char*"}
relop_map = {"=": "==", "<>": "!=", "<": "<", "<=": "<=", ">": ">", ">=": ">=", "==": "=="}
addop_map = {"+": "+", "-": "-", "or": "||"}
mulop_map = {"*": "*", "/": "/", "div": "/", "mod": "%", "and": "&&"}
assignop_map = {":=": "="}
uminus_map = {"-": "-"}


def format_code(code: str) -> str:
    """
    Format the given code using clang-format.

    This function takes a string of code as input, formats it using clang-format with the LLVM style, and returns the
    formatted code as a string.

    Args:
        code (str): The code to be formatted.

    Returns:
        str: The formatted code.
    """
    command = ["clang-format", "-style=llvm"]
    process = subprocess.Popen(
        command,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
    )
    formatted_code, _ = process.communicate(code)
    return formatted_code


def compile_code(code: str, input_ = None, compiler = "gcc") -> str:
    """
    Compile and run the given code.

    This function takes a string of code as input, writes it to a temporary file, compiles it using the specified
    compiler (default is gcc), and runs the resulting executable. If an input is provided, it is passed to the
    executable during its execution. The function returns the stdout of the executable if it runs successfully, or an
    error message if the compilation or execution fails.

    Args:
        code (str): The code to be compiled and run.
        input_ (str, optional): The input to be passed to the executable. Defaults to None.
        compiler (str, optional): The compiler to be used. Defaults to "gcc".

    Returns:
        str: The stdout of the executable if it runs successfully, or an error message if the compilation or execution fails.
    """
    with tempfile.NamedTemporaryFile(suffix = ".c", delete = False) as source_file:
        source_file.write(code.encode())
        source_file.flush()
        source_file_path = source_file.name
    executable_path = source_file_path[:-2]
    compile_command = [compiler, source_file_path, "-o", executable_path, "-lm"]
    compile_process = subprocess.run(
        compile_command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
    )
    if compile_process.returncode != 0:
        return f"Compilation failed:\n{compile_process.stderr}"
    run_command = [executable_path]
    run_process = subprocess.Popen(
        run_command,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
    )
    if input_:
        stdout, stderr = run_process.communicate(input_)
    else:
        stdout, stderr = run_process.communicate()
    if run_process.returncode != 0:
        return f"Runtime error:\n{stderr}"
    return stdout


class Status(Enum):
    NORMAL = 0
    SINGLE_QUOTE = 1
    DOUBLE_QUOTE = 2
    COMMENT = 3


def is_inside_quote(s, idx):
    """
    Check if the character at the given index is inside a quote.

    Args:
    - s (str): The input string.
    - idx (int): The index of the character to check.

    Returns:
    - bool: True if the character is inside a quote, False otherwise.
    """
    in_quote = False
    for i in range(idx):
        if s[i] == '"' and (i == 0 or s[i - 1] != '\\'):
            in_quote = not in_quote
    return in_quote


def convert_to_lower_except_literals(code):
    """
    Convert the input code to lowercase except for string and character literals.

    Args:
    - code (str): The input Pascal code.

    Returns:
    - str: The converted code.
    """
    converted_code = ''
    in_char_literal = False
    in_string_literal = False

    for i, char in enumerate(code):
        if char == "'" and (i == 0 or code[i - 1] != '\\') and not in_string_literal:
            in_char_literal = not in_char_literal
        elif char == '"' and (i == 0 or code[i - 1] != '\\') and not in_char_literal:
            in_string_literal = not in_string_literal

        if not in_char_literal and not in_string_literal:
            converted_code += char.lower()
        else:
            converted_code += char

    return converted_code


def preprocess(code: str) -> str:
    """
    Preprocess the given code.

    This function removes comments from the code and converts all characters to lowercase except for string and character literals.

    Args:
        code (str): The code to be preprocessed.

    Returns:
        str: The preprocessed code.
    """
    code_without_comments = re.sub(r"\{.*?}", "", code, flags = re.DOTALL)
    code_without_comments = convert_to_lower_except_literals(code_without_comments)
    return code_without_comments


def postprocess(tokens: list) -> list:
    """
    Postprocess the given list of tokens.

    This function removes consecutive semicolons from the list of tokens.

    Args:
        tokens (list): The list of tokens to be postprocessed.

    Returns:
        list: The postprocessed list of tokens.
    """
    new_tokens = []
    pre_quote = False
    for token in tokens:
        if token == ";":
            if not pre_quote:
                new_tokens.append(token)
            pre_quote = True
        else:
            new_tokens.append(token)
            pre_quote = False

    return new_tokens


def ensure_strings(func):
    """
    Decorator to ensure that the output of a function is a list of strings.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    def wrapper(node: Tree, context: Context):
        tokens = func(node, context)
        for token in tokens:
            if not isinstance(token, str):
                raise TypeError("Expected token to be a string, but got {}".format(type(token)))
        return tokens

    return wrapper


def ensure_list_of_strings(func):
    """
    Decorator to ensure that the output of a function is a list of strings or a tuple where the first element is a list of strings.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        flag = False
        if isinstance(result, tuple):
            if not isinstance(result[0], list) or not all(isinstance(item, str) for item in result[0]):
                flag = True
        elif not isinstance(result, list) or not all(isinstance(item, str) for item in result):
            flag = True
        if flag:
            raise TypeError("Tokens must be strings")
        return result

    return wrapper


def code_analyze(code: str) -> str:
    """
    Analyze the given code using clang.

    This function writes the code to a temporary file, compiles it using clang with the --analyze option, and returns the stdout or stderr of the process.

    Args:
        code (str): The code to be analyzed.

    Returns:
        str: The stdout or stderr of the clang process.
    """
    with tempfile.NamedTemporaryFile(mode = 'w', suffix = '.c', delete = False) as tmp_file:
        tmp_file.write(code)
        tmp_file_name = tmp_file.name

    command = ["clang", "-c", "--analyze", tmp_file_name]

    process = subprocess.Popen(
        command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
    )

    stdout, stderr = process.communicate()

    try:
        import os
        os.remove(tmp_file_name)
    except Exception as e:
        print(f"Failed to delete temporary file: {e}")

    return stdout or stderr
