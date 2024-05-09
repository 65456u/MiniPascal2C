from mp2c import Converter

parser = Converter()
with open("example.pas") as f:
    code = f.read()
tree, tokens, result_string = parser(code)
