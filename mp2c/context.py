from collections import deque

class Context:
    def __init__(self):
        self.current_scope_index = -1
        self.symbol_table = deque()

    def enter_scope(self):
        self.symbol_table.append({"value" : {}, "array" : {}, "subprogram" : {}})
        self.current_scope_index += 1

    def exit_scope(self):
        self.symbol_table.pop()
        self.current_scope_index -= 1

    def register_func(self, name, header, tokens):
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table) :
            raise Exception("try to register function {} in no scope ".format(name))
        functions_in_top_smbltab = self.symbol_table[self.current_scope_index]["subprogram"]
        functions_in_top_smbltab[name] = FunctionSymbol(name,header,tokens)

    def register_value(self, name, type, mutable, value = None):
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to register value {} in no scope ".format(name))
        values_in_top_smbltab = self.symbol_table[self.current_scope_index]["value"]
        values_in_top_smbltab[name] = ValueSymbol(name, type, mutable, value)

    def register_array(self, name, type, periods):   # periods(start, last) : [[1, 5], [2, 4]]  
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to register array {} in no scope ".format(name))
        arrays_in_top_smbltab = self.symbol_table[self.current_scope_index]["array"]
        dimensions = []
        for dimension in periods:
            dimensions = [dimension[1] - dimension[0] + 1, dimension[0]]
        arrays_in_top_smbltab[name] = ArraySymbol(name, type, dimensions)   # dimensions(length, start) : [[5, 1], [3, 2]]
        
    def get_funcs(self):
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to get functions in no scope ")
        return self.symbol_table[self.current_scope_index]["subprogram"]
    
    def get_values(self):
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to get values in no scope ")
        return self.symbol_table[self.current_scope_index]["value"]
    
    def get_arrays(self):
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to get arrays in no scope ")
        return self.symbol_table[self.current_scope_index]["array"]
    
    # def cname_to_type(self, name):
    #     res = int
    #     if name == "float" :
    #         res = float
    #     elif name == "char" or name == "char*":
    #         res = str
    #     elif name == "bool":
    #         res = bool
    #     return res


class FunctionSymbol:
    def __init__(self, name, header, tokens):
        self.name = name
        self.header = header
        self.tokens = tokens

class ValueSymbol:
    def __init__(self, name, type, mutable, value):
        self.name = name
        self.type = type
        self.mutable = mutable
        self.value = value

class ArraySymbol:
    def __init__(self, name, type, dimensions):
        self.name = name
        self.type = type
        self.dimensions = dimensions    # [[length1, start1], [length2, start2]...]
        length_sum = 0
        for dimension in self.dimensions:
            length_sum += dimension[0]
        self.value = [None] * length_sum

