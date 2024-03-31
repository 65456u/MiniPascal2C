from typing import Any
import lark
from lark import Lark, Transformer, v_args
rules=r"""
%import common.DIGIT
%import common.LETTER
%import common.WS
programstruct            : program_head ";" program_body "."
program_head              : "program" id "(" idlist ")"
                          | "program" id
idlist                   : id
                          | idlist "," id
program_body             : const_declarations var_declarations subprogram_declarations compound_statement
const_declarations       : empty
                          | "const" const_declaration ";"
const_declaration        : id "=" const_value
                          | const_declaration ";" id "=" const_value
const_value              : "+" num
                          | "-" num
                          | num
                          | "'" LETTER "'"
var_declarations         : empty
                          | "var" var_declaration ";"
var_declaration          : idlist ":" type
                          | var_declaration ";" idlist ":" type
type                     : basic_type
                          | "array" "[" period "]" "of" basic_type
basic_type               : "integer"
                          | "real"
                          | "boolean"
                          | "char"
period                   : digits ".." digits
                          | period "," digits ".." digits

subprogram_declarations  : empty
                          | subprogram_declarations subprogram ";"
subprogram                : subprogram_head ";" subprogram_body
subprogram_head           : "procedure" id formal_parameter
                          | "function" id formal_parameter ":" basic_type
formal_parameter         : empty
                          | "(" parameter_list ")"
parameter_list           : parameter
                          | parameter_list ";" parameter
parameter                : var_parameter
                          | value_parameter
var_parameter            : "var" value_parameter
value_parameter          : idlist ":" basic_type
subprogram_body          : const_declarations var_declarations compound_statement
compound_statement       : "begin" statement_list "end"
statement_list           : statement
                          | statement_list ";" statement
statement                : empty
                          | variable assignop expression
                          | func_id assignop expression
                          | procedure_call
                          | compound_statement
                          | "if" expression "then" statement else_part
                          | "for" id assignop expression "to" expression "do" statement
                          | "while" expression "do" statement
                          | "read\(" variable_list ")"
                          | "write\(" expression_list ")"
variable_list            : variable
                          | variable_list "," variable
variable                 : id id_varpart
id_varpart               : empty
                          | "[" expression_list "]"
procedure_call           : id
                          | id "(" expression_list ")"
else_part                : empty
                          | "else" statement
expression_list          : expression
                          | expression_list "," expression
expression               : simple_expression
                          | simple_expression relop simple_expression
simple_expression        : term
                          | simple_expression addop term
term                     : factor
                          | term mulop factor
factor                   : num
                          | variable
                          | "(" expression ")"
                          | "not" factor
                          | uminus factor
                          | func_id "(" expression_list ")"

digits                   : DIGIT+
id                     : LETTER (LETTER | DIGIT)*
optional_fraction     : empty
                        | "." digits
num                   : digits optional_fraction
relop                 : "="
                        | "<>"
                        | "<"
                        | "<="
                        | ">"
                        | ">="
addop                 : "+"
                        | "-"
                        | "or"
mulop                 : "*"
                        |"/"
                        | "div"
                        | "mod"
                        | "and"
assignop              : ":="
empty                 : WS*
func_id               : id
uminus                : "-"

%ignore WS
"""
class MP2CParser():
    def __init__(self):
        self.parser = Lark(rules, start='programstruct')

    def __call__(self, code) -> Any:
        return self.parser.parse(code).pretty()

    