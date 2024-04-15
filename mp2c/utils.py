import subprocess

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
