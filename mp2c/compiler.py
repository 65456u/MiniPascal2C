import subprocess
from typing import Any

import clang_format


class Compiler:
    def __init__(self, parser) -> None:
        self.parser = parser

    def __call__(self, code: str) -> Any:
        tree = self.parser(code)
        tokens = []
        tokens = self.visit_programstruct(tree, tokens)
        # concatenate tokens into a string
        result_string = ""
        for token in tokens:
            result_string += token
        # format the string using clang_format
        return clang_format.format_code(result_string)

    def format_code(code: str) -> str:
        # clang-format命令
        command = ['clang-format', '-style=llvm']

        # 启动子进程
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)

        # 将代码写入stdin并获取格式化后的代码
        formatted_code, _ = process.communicate(code)

        return formatted_code
