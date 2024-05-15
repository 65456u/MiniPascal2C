import functools
import re
import subprocess
import tempfile

from lark.lark import Tree

from .context import Context
from .errors import VisitingError

type_map = {"integer": "int", "real": "float", "boolean": "bool", "char": "char"}
relop_map = {"=": "==", "<>": "!=", "<": "<", "<=": "<=", ">": ">", ">=": ">="}
addop_map = {"+": "+", "-": "-", "or": "||"}
mulop_map = {"*": "*", "/": "/", "div": "/", "mod": "%", "and": "&&"}
assignop_map = {":=": "="}
uminus_map = {"-": "-"}


def format_code(code: str) -> str:
    # clang-format命令
    command = ["clang-format", "-style=llvm"]

    # 启动子进程
    process = subprocess.Popen(
        command,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
    )

    # 将代码写入stdin并获取格式化后的代码
    formatted_code, _ = process.communicate(code)

    return formatted_code


def compile_code(code: str, input_ = None) -> str:
    # 创建临时文件来存储代码
    with tempfile.NamedTemporaryFile(suffix = ".c", delete = False) as source_file:
        source_file.write(code.encode())  # 将字符串编码为字节对象
        source_file.flush()
        source_file_path = source_file.name

    # 编译代码
    executable_path = source_file_path[:-2]  # 去掉 .c 后缀
    compile_command = ["gcc", source_file_path, "-o", executable_path]
    compile_process = subprocess.run(
        compile_command,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
    )

    if compile_process.returncode != 0:
        return f"Compilation failed:\n{compile_process.stderr}"

    # 运行代码
    run_command = [executable_path]
    run_process = subprocess.Popen(
        run_command,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
    )

    # 如果有输入，写入stdin
    if input_:
        stdout, stderr = run_process.communicate(input_)
    else:
        stdout, stderr = run_process.communicate()

    if run_process.returncode != 0:
        return f"Runtime error:\n{stderr}"

    return stdout


def preprocess(code: str) -> str:
    # 去除形如 {...} 的注释
    code_without_comments = re.sub(r"\{.*?}", "", code, flags = re.DOTALL)

    # 将代码转换成小写
    code_without_comments = code_without_comments.lower()

    return code_without_comments


def postprocess(tokens: list) -> list:
    # 仅保留连续";"中的第一个
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


def error_recorder(info):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except VisitingError as e:
                message = e.message
                message += info
                raise VisitingError(message)

        return wrapper

    return decorator
