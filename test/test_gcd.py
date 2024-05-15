from mp2c import Converter, compile_code


class TestGCD:
    def test_gcd(self):
        gcd_test_code = r"""
        program example(input, output);

        var
          x, y: integer;
        
        function gcd(a, b: integer): integer;
        begin
          if b = 0 then
            gcd := a
          else
            gcd := gcd(b, a mod b);
        end;
        
        begin
          read(x, y);
          writeln(gcd(x, y));
        end.
        """
        converter = Converter()
        success, result = converter(gcd_test_code, debug = True)
        print(result)
        output = compile_code(result, "6 9\n")
        assert output == "3\n"
