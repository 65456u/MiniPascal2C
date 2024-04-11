from typing import Any

from utils import format_code


class Compiler:
    def __init__(self, parser) -> None:
        self.parser = parser

    def __call__(self, code: str) -> Any:
        tree = self.parser(code)
        tokens = []
        tokens = self.visit_programstruct(tree, tokens)
        # concatenate tokens into a string
        result_string = "   ".join(tokens)
        # format the string using clang_format
        return format_code(result_string)

    def visit_programstruct(self, tree, tokens):
        for node in tree.children:
            if node.data == "program":
                tokens.append("int main() {\n")
                tokens = self.visit_program(node, tokens)
                tokens.append("}\n")
        return tokens
