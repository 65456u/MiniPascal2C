import mp2c

array_test_code = r"""
program ArrayTest1;

var
  arr: array[1..10] of integer;
  i: real;

begin
  arr[i] := 1;
end.
"""
converter = mp2c.Converter()
result = converter.convert(array_test_code, debug = True)
print(result.success)
print(result.code)
print(result.error_messages)
print(result.error_info)

fuck_test_code = r"""
fuck
"""
result = converter.convert(fuck_test_code, debug = True)
print(result.success)
print(result.code)
for message in result.error_messages:
    print(message)
print(result.error_info)
