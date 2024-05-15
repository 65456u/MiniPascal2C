from mp2c import Converter, compile_code

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


class TestArray:
    def test_array(self):
        converter = Converter()
        success, result = converter(array_test_code, debug = True)
        output = compile_code(result)
        assert output == "12345678910"
