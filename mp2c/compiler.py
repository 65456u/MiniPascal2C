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
            if node.data == "program_head":
                self.visit_program_head(node, tokens)
            elif node.data == "program_body":
                self.visit_program_body(node, tokens)
        tokens.append("}\n")
        return tokens
    

    def visit_program_head(self, node, tokens):
        program_name = node.children[0].data
        tokens.append("#pragma once\n")
        tokens.append("#ifndef _" + program_name.upper() + "_\n")
        tokens.append("#define _" + program_name.upper() + "_\n")
        tokens.append("#include <iostream>")
    

    def visit_program_body(self, node, tokens):
        for child in node.children:
            if(child.data == "const_declarations"):
                self.visit_const_declarations(child, tokens)
            elif (child.data == "var_declarations"):
                self.visit_var_declarations(child, tokens)
            elif (child.data == "subprogram_declarations"):
                self.visit_subprogram_declarations(child, tokens)
            elif (child.data == "compound_statement"):
                tokens.append("int main()\n")
                self.visit_compound_statement(child, tokens)

    
    def visit_const_declaration(self, node, tokens):
        for child in node.children:
            if(child.data == "const_declaration"):
                self.visit_const_declaration(child, tokens)
                tokens.append(";\n")
            elif (child.data == "id"):
                tokens.append("const ")
                tokens.append("double ")
                tokens.append(child.data + " = ")
            elif (child.data == "const_value"):
                tokens.append(child.data)
    
    def visit_var_declarations(self, node, tokens):
        for child in node.children:
            if(child.data == "empty"):
                return tokens
            else:
                self.visit_var_declaration(child, tokens)
                tokens.append(";\n")
                return tokens
        
    # 返回(False)表示类型为basic_type，返回(True, 5)表示类型为数组，长度为5
    def visit_type(self, node, tokens):
        for child in node.children:
            if(child.data == "basic_type"):
                self.visit_basic_type(child, tokens)
                return (False)
            else:
                self.visit_basic_type(child, tokens)
                length = self.visit_period(child, tokens)
                return (True, length)


    def visit_period(self, node, tokens):
        length = 0
        skip = False
        for child in node.children:
            if(child.data == "period"):
                length += self.visit_period(child, tokens)
            elif(child.data == "digits"):
                if(not skip):
                    skip = True
                    length -= int(child.children[0].data)
                elif (skip):
                    skip = False
                    length += int(child.children[0].data)
        return length

    def visit_subprogram(self, node, tokens):
        for child in node.chilren:
            if(child.data == "subprogram_head"):
                self.visit_subprogram_head()
            elif(child.data == "subprogram_body"):
                self.visit_subprogram_boty()

    def visit_formal_parameter(self, node, tokens):
        for child in node.children:
            if(child.data == "empty"):
                return
            else:
                tokens.append("(")
                self.visit_parameter_list(child, tokens)
                tokens.append(")")

    def visit_parameter(self, node, tokens):
        for child in node.children:
            if(child.data == "var_parameter"):
                self.visit_var_parameter(child, tokens)
            else:
                self.visit_value_parameter(child, tokens)

    def visit_value_parameter(self, node, tokens):
        self.visit_basic_type(node.children[1], tokens)
        tokens.append(" ")
        self.visit_idlist(node.children[0], tokens)

    def visit_compound_statement(self, node, tokens):
        tokens.append("{\n")
        self.visit_statement_list(node.children[0], tokens)
        tokens.append("}\n")

    def visit_statement(self, node, tokens):
        if node.children[0].data == "variable":
            self.visit_variable(node.children[0], tokens)
            tokens.append(node.children[1].children[0].value)
            self.visit_expression(node.children[2], tokens)
        elif node.children[0].data == "func_id":
            self.visit_func_id(node.children[0], tokens)
            tokens.append(node.children[1].children[0].value)
            self.visit_expression(node.children[2], tokens)
        elif node.children[0].data == "procedure_call":
            self.visit_procedure_call(node.children[0], tokens)
        elif node.children[0].data == "compound_statement":
            self.visit_compound_statement(node.children[0], tokens)
        elif node.children[0].data == "expression" and len(node.children) == 3:
            tokens.append("if (")
            self.visit_expression(node.children[0], tokens)
            tokens.append("){\n")
            self.visit_statement(node.children[1], tokens)
            tokens.append("}")
            self.visit_else_part(node.children[2], tokens)
        elif node.children[0].data == "id":
            tokens.append("for ( int ")
            name = node.children[0].children[0].value
            tokens.append(name)
            tokens.append(node.children[1].children[0].value)
            self.visit_expression(node.children[2])
            tokens.append("; {name} <= ")
            self.visit_expression(node.children[3])
            tokens.append("{\n")
            self.visit_statement(node.children[4], tokens)
            tokens.append("}\n")
        elif node.children[0].data == "expression" and len(node.children) == 2:
            tokens.append("while(")
            self.visit_expression(node.children[0])
            tokens.append("{\n")
            self.visit_statement(node.children[1], tokens)
            tokens.append("}\n")
        elif node.children[0].data == "variable_list":
            tokens.append("std::cin >> ")
            # True表示希望visit_variable_list函数输出的内容用>>代替,
            self.visit_variable_list(node.children[0], tokens, True)
            tokens.append(";\n")
        elif node.children[0].data == "expression_list":
            tokens.append("std::cout << ")
            # True表示希望visit_expression_list函数输出的内容用<<代替,
            self.visit_expression_list(node.children[0], tokens, True)
            tokens.append(";\n")     




    def visit_variable(self, node, tokens):
        tokens.append(node.children[0].children[0].value)
        if(node.children[1].data == "expression_list"):
            tokens.append("[")
            self.visit_expression_list(node.children[1].children[0], tokens)
            tokens.append("]")

    def visit_procedure_call(self, node, tokens):
        if len(node.children) == 1:
            tokens.append(node.children[0].children[0].value)
            tokens.append("()")
        else:
            tokens.append(node.children[0].children[0].value)
            tokens.append("(")
            self.visit_expression_list(node.children[1], tokens)
            tokens.append(")")

    def visit_expression_list(self, node, tokens):
        for child in node.children:
            if(child.data == "expression_list"):
                self.visit_expression_list(child, tokens)
                tokens.append(", ")
            else:
                self.visit_expression(child, tokens)
    
    def visit_simple_expression(self, node, tokens):
        for child in node.children:
            if(child.data == "simple_expression"):
                self.visit_simple_expression(child, tokens)
            elif child.data == "addop":
                tokens.append(child.children[0].value)
            elif child.data == "term":
                self.visit_term(child, tokens)

    def visit_factor(self, node, tokens):
        for child in node.chilren:
            if child.data == "variable":
                self.visit_variable(child, tokens)
            elif child.data == "num":
                self.visit_num(child, tokens)
            elif child.data == "expression":
                tokens.append("(")
                self.visit_expression(child, tokens)
                tokens.append(")")
            elif child.data == "factor":
                tokens.append("!")
                self.visit_factor(child, tokens)
            elif child.data == "uminus":
                tokens.append("-")
                self.visit_factor(node.children[1], tokens)
                return
            elif child.data == "func_id":
                tokens.append(child.children[0].children[0].value + "(")
                self.visit_expression_list(child, tokens)
                tokens.append(")")
                return

    def visit_num(self, node, tokens):
        for child in node:
            if(child.data == "digits"):
                tokens.append(str(child.children[0].value))
            elif child.data == "optional_fraction":
                if child.children[0].data == "digits":
                    tokens.append(".")
                    tokens.append(str(child.children[0].children[0].value))

    
