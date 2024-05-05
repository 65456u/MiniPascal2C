import subprocess
import re

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
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # 将代码写入stdin并获取格式化后的代码
    formatted_code, _ = process.communicate(code)

    return formatted_code


def preprocess(code: str) -> str:
    # 去除形如 {...} 的注释
    code_without_comments = re.sub(r"\{.*?\}", "", code, flags=re.DOTALL)

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