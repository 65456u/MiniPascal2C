identifier_test_code = r"""
program IdentifierTest(input, output);
var
  a, b2, _temp, MyVariable: integer;
begin
  { 测试合法和非法标识符 }
end.
"""

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

char_test_code = r"""
program CharTest;
const
    c1 = 'a';
    c2 = '''';
begin
  write(c1, c2);
end.
"""
operator_test_code = r"""
program OperatorTest;
var
  a, b: integer;
begin
  a := 10;
  b := 3;
  write(a + b);
  write(a - b);
  write(a * b);
  write(a / b);
  write(a div b);
  write(a mod b);
end.
"""

comment_test_code = r"""
program CommentTest;
{ 这是一个程序注释 }

var
  x: integer; { 这是一个变量注释 }

begin
  x := 42; { 计算 }
end.
"""

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
scope_test_code = r"""
program VariableScope;

var
  globalVar: integer;

procedure LocalScope;
var
  localVar: integer;
begin
  globalVar := 10;
  localVar := 20;
end;

begin
  globalVar := 5;
  LocalScope;
  write(globalVar);  { Output: 10 }
  write(localVar);   { Compilation error: localVar not defined in this scope }
end.
"""
scope_test_code2 = r"""
program ScopeTest;

var
    globalVar: integer;

procedure PrintGlobal;
var
    localVar: integer;
begin
    localVar := 10;
    write(globalVar);
    write(localVar);
end;

procedure ModifyGlobal;
var
    localVar: integer;
begin
    localVar := 20;
    globalVar := localVar;
end;

var
    localVar: integer;
begin
    localVar := 5;
    write(localVar);
    write(globalVar);
    PrintGlobal;
    ModifyGlobal;
    write(globalVar);
end.
"""