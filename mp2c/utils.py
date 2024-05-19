import functools
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


def preprocess(code: str) -> str:
    code_without_comments = re.sub(r"\{.*?}", "", code, flags = re.DOTALL)
    code_without_comments = code_without_comments.lower()
    return code_without_comments


def postprocess(tokens: list) -> list:
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
    def wrapper(node: Tree, context: Context):
        tokens = func(node, context)
        for token in tokens:
            if not isinstance(token, str):
                raise TypeError("Expected token to be a string, but got {}".format(type(token)))
        return tokens

    return wrapper




def ensure_list_of_strings(func):
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
