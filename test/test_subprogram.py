from mp2c import Converter, compile_code


class TestSubprogram:
    def test_multiple_subprogram(self):
        msp_code = r"""
        program example(input, output);
        var x: integer;
            y: integer;
        function a(): integer;
        begin
            a := 1;
        end;
        function b(): integer;
        begin
            b := 2;
        end;
        begin
            writeln(a());
            writeln(b());
        end.
        """
        converter = Converter()
        success, result = converter(msp_code, debug = True)
        output = compile_code(result)
        assert output == "1\n2\n"

    def test_procedure(self):
        procedure_code = r"""
        program example(input, output);
        var x: integer;
            y: integer;
        procedure a();
        begin
            writeln(1);
        end;
        procedure b();
        begin
            writeln(2);
        end;
        begin
            a;
            b;
        end.
        """
        converter = Converter()
        success, result = converter(procedure_code, debug = True)
        output = compile_code(result)
        assert output == "1\n2\n"

    def test_function_with_parameter(self):
        fwp_code = r"""
        program example(input, output);
        var x: integer;
            y: integer;
        function a(x: integer): integer;
        begin
            a := x;
        end;
        begin
            writeln(a(1));
            writeln(a(2));
        end.
        """
        converter = Converter()
        success, result = converter(fwp_code, debug = True)
        output = compile_code(result)
        assert output == "1\n2\n"

    def test_procedure_with_parameter(self):
        pwp_code = r"""
        program example(input, output);
        var x: integer;
            y: integer;
        procedure a(x: integer);
        begin
            writeln(x);
        end;
        begin
            a(1);
            a(2);
        end.
        """
        converter = Converter()
        success, result = converter(pwp_code, debug = True)
        output = compile_code(result)
        assert output == "1\n2\n"
