from mp2c import Converter, compile_code


class TestMath:
    def test_add(self):
        add_test_code = r"""
        program test(input, output);
        var
            a, b: integer;
        begin
            a := 10;
            b := 20;
            writeln(a + b);
        end.
        """

        converter = Converter()
        success, result = converter(add_test_code, debug = True)
        output = compile_code(result)
        assert output == "30\n"

    def test_sub(self):
        sub_test_code = r"""
        program test(input, output);
        var
            a, b: integer;
        begin
            a := 10;
            b := 20;
            writeln(a - b);
        end.
        """

        converter = Converter()
        success, result = converter(sub_test_code, debug = True)
        output = compile_code(result)
        assert output == "-10\n"

    def test_mul(self):
        mul_test_code = r"""
        program test(input, output);
        var
            a, b: integer;
        begin
            a := 10;
            b := 20;
            writeln(a * b);
        end.
        """

        converter = Converter()
        success, result = converter(mul_test_code, debug = True)
        output = compile_code(result)
        assert output == "200\n"

    def test_div(self):
        div_test_code = r"""
        program test(input, output);
        var
            a, b: integer;
        begin
            a := 10;
            b := 20;
            writeln(a / b);
        end.
        """

        converter = Converter()
        success, result = converter(div_test_code, debug = True)

        output = compile_code(result)
        assert output == "0.500000\n"

    def test_mod(self):
        mod_test_code = r"""
        program test(input, output);
        var
            a, b: integer;
        begin
            a := 10;
            b := 20;
            writeln(a mod b);
        end.
        """

        converter = Converter()
        success, result = converter(mod_test_code, debug = True)
        output = compile_code(result)
        assert output == "10\n"

    def test_acos(self):
        acos_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(acos(a));
        end.
        """
        converter = Converter()
        success, result = converter(acos_test_code, debug = True)

        output = compile_code(result)
        assert output == "1.047198\n"

    def test_asin(self):
        asin_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(asin(a));
        end.
        """
        converter = Converter()
        success, result = converter(asin_test_code, debug = True)

        output = compile_code(result)
        assert output == "0.523599\n"

    def test_atan(self):
        atan_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(atan(a));
        end.
        """
        converter = Converter()
        success, result = converter(atan_test_code, debug = True)

        output = compile_code(result)
        assert output == "0.463648\n"

    def test_cos(self):
        cos_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(cos(a));
        end.
        """
        converter = Converter()
        success, result = converter(cos_test_code, debug = True)

        output = compile_code(result)
        assert output == "0.877583\n"

    def test_sin(self):
        sin_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(sin(a));
        end.
        """
        converter = Converter()
        success, result = converter(sin_test_code, debug = True)
        output = compile_code(result)
        assert output == "0.479426\n"

    def test_tanh(self):
        tanh_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(tanh(a));
        end.
        """
        converter = Converter()
        success, result = converter(tanh_test_code, debug = True)
        output = compile_code(result)
        assert output == "0.462117\n"

    def test_exp(self):
        exp_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(exp(a));
        end.
        """
        converter = Converter()
        success, result = converter(exp_test_code, debug = True)
        output = compile_code(result)
        assert output == "1.648721\n"

    def test_log(self):
        log_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(log(a));
        end.
        """
        converter = Converter()
        success, result = converter(log_test_code, debug = True)

        output = compile_code(result)
        assert output == "-0.693147\n"

    def test_log10(self):
        log10_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(log10(a));
        end.
        """
        converter = Converter()
        success, result = converter(log10_test_code, debug = True)
        output = compile_code(result)
        assert output == "-0.301030\n"

    def test_sqrt(self):
        sqrt_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(sqrt(a));
        end.
        """
        converter = Converter()
        success, result = converter(sqrt_test_code, debug = True)
        output = compile_code(result)
        assert output == "0.707107\n"

    def test_ceil(self):
        ceil_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(ceil(a));
        end.
        """
        converter = Converter()
        success, result = converter(ceil_test_code, debug = True)
        output = compile_code(result)
        assert output == "1.000000\n"

    def test_fabs(self):
        fabs_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := -0.5;
            writeln(fabs(a));
        end.
        """
        converter = Converter()
        success, result = converter(fabs_test_code, debug = True)
        output = compile_code(result)
        assert output == "0.500000\n"

    def test_floor(self):
        floor_test_code = r"""
        program test(input, output);
        var
            a: real;
        begin
            a := 0.5;
            writeln(floor(a));
        end.
        """
        converter = Converter()
        success, result = converter(floor_test_code, debug = True)
        output = compile_code(result)
        assert output == "0.000000\n"
