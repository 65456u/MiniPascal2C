from mp2c import Converter, compile_code


class TestComprehensive:
    def test_gcd(self):
        gcd_test_code = r"""
        program example(input, output);

        var
          x, y: integer;
          z, h: real;
          a: real;
          arr: array[1..10] of integer;
        
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
        output = compile_code(result, "6 9\n")
        assert output == "3\n"

    def test_fib(self):
        fib_test_code = r"""
        program example(input, output);
        
        var
          x: integer;
        
        function fib(n: integer): integer;
        begin
          if n = 0 then
            fib := 0
          else if n = 1 then
            fib := 1
          else
            fib := fib(n - 1) + fib(n - 2);
        end;
        
        begin
          read(x);
          writeln(fib(x));
        end.
        """
        converter = Converter()
        success, result = converter(fib_test_code, debug = True)
        output = compile_code(result, "10\n")
        assert output == "55\n"

    def test_bubblesort(self):
        bubblesort_test_code = r"""
        program test(input, output);
        var
            i: integer;
            a: array[1..10] of integer;

        procedure swap(var x, y: integer);
        var
            tmp: integer;
        begin
            tmp := x;
            x := y;
            y := tmp;
        end;

        procedure bubbleSort;
        var
            i, j: integer;
        begin
            for i := 1 to 10 do
            begin
                for j := i + 1 to 10 do
                begin
                    if a[i] > a[j] then
                        swap(a[i], a[j]);
                end;
            end;
        end;

        begin
            i := 1;
            while i <= 10 do
            begin
                read(a[i]);
                i := i + 1;
            end;
            bubbleSort;
            for i := 1 to 10 do
                write(a[i]);
            writeln;
        end.
            """
        converter = Converter()
        success, result = converter(bubblesort_test_code, debug = True)
        print(result)
        output = compile_code(result, "10 9 8 7 6 5 4 3 2 1\n")
        assert output == "12345678910\n"

    def test_quicksort(self):
        quicksort_test_code = r"""
        program test(input, output);
        var
            i: integer;
            a: array[1..10] of integer;
        
        procedure quickSort(left, right: integer);
        var
            i, j, x, y: integer;
        begin
            i := left;
            j := right;
            x := a[(left + right) div 2];
            while i <= j do
            begin
                while a[i] < x do
                    i := i + 1;
                while a[j] > x do
                    j := j - 1;
                if i <= j then
                begin
                    y := a[i];
                    a[i] := a[j];
                    a[j] := y;
                    i := i + 1;
                    j := j - 1;
                end;
            end;
            if left < j then
                quickSort(left, j);
            if i < right then
                quickSort(i, right);
        end;
        
        begin
            i := 1;
            while i <= 10 do
            begin
                read(a[i]);
                i := i + 1;
            end;
            quickSort(1, 10);
            for i := 1 to 10 do
                write(a[i]);
            writeln;
        end.
        """
        converter = Converter()
        success, result = converter(quicksort_test_code, debug = True)
        output = compile_code(result, "10 9 8 7 6 5 4 3 2 1\n")
        assert output == "12345678910\n"
