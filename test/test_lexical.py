import pytest

from mp2c import Converter, compile_code


class TestLexical:
    def test_lexical_identifier(self):
        identifier_test_code = r"""
        program IdentifierTest(input, output);
        var
          a, b2, _temp, MyVariable: integer;
        begin
          { 测试合法和非法标识符 }
        end.
        """
        converter = Converter()
        success, result = converter(identifier_test_code, debug = True)
        output = compile_code(result)
        assert output == ""

    def test_lexical_keyword(self):
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
        converter = Converter()
        success, result = converter(keyword_test_code, debug = True)
        output = compile_code(result)
        assert output == "p"

    def test_lexical_number(self):
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
        converter = Converter()
        success, result = converter(number_test_code, debug = True)
        output = compile_code(result)
        assert output == "123-4563.140000-0.618000"

    def test_lexical_char(self):
        char_test_code = r"""
        program CharTest;
        const
            c1 = 'a';
            c2 = '''';
        begin
          write(c1, c2);
        end.
        """
        converter = Converter()
        with pytest.raises(Exception):
            success, result = converter(char_test_code, debug = True)

    def test_lexical_operator(self):
        operator_test_code = r"""
        program OperatorTest;
        var
          a, b: integer;
        begin
          a := 10;
          b := 3;
          writeln(a + b);
          writeln(a - b);
          writeln(a * b);
          writeln(a / b);
          writeln(a div b);
          writeln(a mod b);
        end.
        """
        converter = Converter()
        success, result = converter(operator_test_code, debug = True)
        output = compile_code(result)
        assert output == "13\n7\n30\n3.333333\n3\n1\n"

    def test_lexical_comment(self):
        comment_test_code = r"""
        program CommentTest;
        { 这是一个程序注释 }

        var
          x: integer; { 这是一个变量注释 }

        begin
          x := 42; { 计算 }
        end.
        """
        converter = Converter()
        success, result = converter(comment_test_code, debug = True)
        output = compile_code(result)
        assert output == ""
