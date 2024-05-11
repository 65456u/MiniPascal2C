from mp2c import Converter

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
success, result = converter(array_test_code, debug=True)
print(result)
