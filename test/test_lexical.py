from mp2c import Converter

identifier_test_code = r"""
program IdentifierTest(input, output);
var
  a, b2, _temp, MyVariable: integer;
begin
  { 测试合法和非法标识符 }
end.
"""

keyword_test_code = r"""
program KeywordTest;
const
  Pi = 3.14;
  p = 'p';
  z = 'z';
var
  x: real;

begin
  x := Pi;
  if x > 0 then
    write(p)
  else
    write(z);
end.
"""

number_test_code = r"""
program NumberTest;
const
  A = 123;
  B = -456;
  C = 3.14;
  D = -0.618;
begin
  write(A, B, C, D);
end.
"""

char_test_code = r"""
program CharTest;
const
    c1 = 'a';
    c2 = '''';
begin
  write(c1, c2);
end.
"""
operator_test_code = r"""
program OperatorTest;
var
  a, b: integer;
begin
  a := 10;
  b := 3;
  write(a + b);
  write(a - b);
  write(a * b);
  write(a / b);
  write(a div b);
  write(a mod b);
end.
"""

comment_test_code = r"""
program CommentTest;
{ 这是一个程序注释 }

var
  x: integer; { 这是一个变量注释 }

begin
  x := 42; { 计算 }
end.
"""


class TestLexical:
    def test_lexical_identifier(self):
        converter = Converter()
        success, result = converter(identifier_test_code)
        assert success

    def test_lexical_keyword(self):
        converter = Converter()
        success, result = converter(keyword_test_code)
        assert success

    def test_lexical_number(self):
        converter = Converter()
        success, result = converter(number_test_code)
        assert success

    def test_lexical_char(self):
        converter = Converter()
        success, result = converter(char_test_code)
        assert not success

    def test_lexical_operator(self):
        converter = Converter()
        success, result = converter(operator_test_code)
        assert result

    def test_lexical_comment(self):
        converter = Converter()
        success, result = converter(comment_test_code)
        assert success
