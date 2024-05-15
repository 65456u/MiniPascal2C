from mp2c import Converter, compile_code


def test_scope_success():
    scope_test_code2 = r"""
    program ScopeDemo;

    var
      A: integer;

    procedure ScopeInner;
    var
      A: integer;
    begin
      A := 10;
      write(A);
    end;

    begin
      A := 20;
      write(A);
      ScopeInner;
      write(A);
    end.
    """
    converter = Converter()
    success, result = converter(scope_test_code2, debug = True)
    output = compile_code(result)
    assert output == "201020"


def test_scope_failure():
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
    converter = Converter()
    success, result = converter(scope_test_code)
    assert not success
