from mp2c import Converter, compile_code


class TestControl:
    def test_if_else_simple(self):
        control_test_code = r"""
        program IfElseTest;
        var
            a, b: INTEGER;
        begin
            a := 10;
            b := 20;
            if a > b then
                write(a)
            else
                write(b);
        end.
        """
        converter = Converter()
        success, result = converter(control_test_code, debug = True)
        output = compile_code(result)
        assert output == "20"

    def test_if_else_nested(self):
        control_test_code = r"""
        program IfElseNested;
        var
            a, b: integer;
        begin
            a := 10;
            b := 20;
            if a > b then
                write(a)
            else
                if a < b then
                    write(b)
                else
                    write(0);
        end.
        """
        converter = Converter()
        success, result = converter(control_test_code, debug = True)
        output = compile_code(result)
        assert output == "20"

    def test_for_loop(self):
        control_test_code = r"""
        program ForLoopTest;
        var
            i: integer;
        begin
            for i := 1 to 10 do
                write(i);
        end.
        """
        converter = Converter()
        success, result = converter(control_test_code, debug = True)
        print(result)
        output = compile_code(result)

        assert output == "12345678910"

    def test_while_loop(self):
        control_test_code = r"""
        program WhileLoopTest;
        var
            i: integer;
        begin
            i := 1;
            while i <= 10 do
            begin
                write(i);
                i := i + 1;
            end;
        end.
        """
        converter = Converter()
        success, result = converter(control_test_code, debug = True)
        output = compile_code(result)
        assert output == "12345678910"
