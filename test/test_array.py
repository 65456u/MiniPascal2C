from mp2c import Converter, compile_code


class TestArray:
    def test_array(self):
        array_test_code = r"""
        program ArrayTest1;

        var
          arr: array[1..10] of integer;
          i: integer;

        begin
          { 初始化数组 }
          for i := 1 to 10 do
            arr[i] := i;

          { 访问数组元素 }
          for i := 1 to 10 do
            write(arr[i]);
        end.
        """
        converter = Converter()
        success, result = converter(array_test_code, debug = True)
        output = compile_code(result)
        assert output == "12345678910"

    def test_array_multi_dimension(self):
        array_multi_dimension_test_code = r"""
        program ArrayTest2;

        var
          arr: array[1..10, 1..10] of integer;
          i, j: integer;

        begin
          { 初始化数组 }
          for i := 1 to 10 do
            for j := 1 to 10 do
              arr[i, j] := i * j;

          { 访问数组元素 }
          for i := 1 to 10 do
            for j := 1 to 10 do
              write(arr[i, j]);
        end.
        """

        converter = Converter()
        success, result = converter(array_multi_dimension_test_code, debug = True)
        output = compile_code(result)
        print(output)
        assert (output == "12345678910" +
                "2468101214161820" +
                "36912151821242730" +
                "481216202428323640" +
                "5101520253035404550" +
                "6121824303642485460" +
                "7142128354249566370" +
                "8162432404856647280" +
                "9182736455463728190" +
                "102030405060708090100")
