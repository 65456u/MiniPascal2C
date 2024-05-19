# Grammar rules for MiniPascal
rules = r"""
RELOP                    : EQUAL
                         | "<>"
                         | "<"
                         | "<="
                         | ">"
                         | ">="
EQUAL                    : "="
programstruct            : program_head ";" program_body "."
program_head             : "program" id "(" idlist ")"
                         | "program" id
idlist                   : id
                         | idlist "," id
program_body             : const_declarations var_declarations subprogram_declarations compound_statement
const_declarations       : "const" const_declaration ";"
                         | empty
const_declaration        : id "=" const_value
                         | const_declaration ";" id "=" const_value
const_value              : PLUS num
                         | MINUS num
                         | num
                         | "'" LETTER "'"
PLUS                     : "+"
MINUS                    : "-"        
var_declarations         : "var" var_declaration ";"
                         | empty
var_declaration          : idlist ":" type
                         | var_declaration ";" idlist ":" type
type                     : basic_type
                         | "array" "[" period "]" "of" basic_type
basic_type               : INTEGER
                         | REAL
                         | BOOLEAN
                         | CHAR
                         | STRING
STRING                   : "string"
period                   : DIGITS ".." DIGITS
                         | period "," DIGITS ".." DIGITS
subprogram_declarations  : empty
                         | subprogram ";"
                         | subprogram_declarations subprogram ";"
subprogram               : procedure_declaration | function_declaration
procedure_declaration    : "procedure" id formal_parameter ";" subprogram_body
function_declaration     : "function" id formal_parameter ":" basic_type ";"  subprogram_body
subprogram_body          : const_declarations var_declarations compound_statement
formal_parameter         : "(" parameter_list ")"
                         | empty
parameter_list           : empty
                         | parameter (";" parameter)*
parameter                : var_parameter
                         | value_parameter
var_parameter            : "var" value_parameter
value_parameter          : idlist ":" basic_type
compound_statement       : "begin" statement_list "end"
statement_list           : statement
                         | statement_list ";" statement
statement                : empty
                         | assign_statement
                         | procedure_call
                         | compound_statement
                         | if_else_statement
                         | for_statement
                         | while_statement
                         | repeat_statement
repeat_statement         : "repeat" statement_list "until" expression
assign_statement         : variable ASSIGNOP expression
if_else_statement        : "if" expression "then" statement else_part?
for_statement            : "for" id ASSIGNOP expression "to" expression "do" statement
                         | "for" id ASSIGNOP expression DOWN "to" expression "do" statement
DOWN                     : "down"
while_statement          : "while" expression "do" statement
variable_list            : variable ("," variable)*
variable                 : id id_varpart?
id_varpart               : "[" expression_list "]"
procedure_call           : id
                         | id "(" expression_list ")"
else_part                : "else" statement
expression_list          : expression ("," expression)*
expression               : simple_expression
                         | simple_expression RELOP simple_expression
                         | char_literal
                         | string_literal
char_literal             : "'" LETTER "'"
string_literal           : ESCAPED_STRING
simple_expression        : term
                         | simple_expression ADDOP term
term                     : factor
                         | term MULOP factor
factor                   : num
                         | variable
                         | "(" expression ")"
                         | NOT factor
                         | UMINUS factor
                         | function_call
function_call            : func_id "(" expression_list? ")"
NOT                      : "not"
DIGITS                   : DIGIT+
id                       : IDENTIFIER_TOKEN
optional_fraction        : "." DIGITS
num                      : DIGITS optional_fraction?
ADDOP                    : "+"
                         | "-"
                         | "or"
MULOP                    : "*"
                         | "/"
                         | "div"
                         | "mod"
                         | "and"
ASSIGNOP                 : ":="
empty                    : WS*
func_id                  : id
UMINUS                   : "-"
IDENTIFIER_TOKEN         : /[a-zA-Z_][a-zA-Z0-9_]*/
INTEGER                  : "integer"
REAL                     : "real"
BOOLEAN                  : "boolean"
CHAR                     : "char"
%import common.DIGIT
%import common.LETTER
%import common.WS
%import common.ESCAPED_STRING
%ignore WS
"""
