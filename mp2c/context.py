from collections import deque


class Context:
    def __init__(self):
        self.current_scope_index = -1
        self.symbol_table = deque()
        self.on_error = False
        self.error_messages = []

    def enter_scope(self):
        self.symbol_table.append({"value": {}, "array": {}, "subprogram": {}})
        self.current_scope_index += 1

    def exit_scope(self):
        self.symbol_table.pop()
        self.current_scope_index -= 1

    def register_func(self, name, header, parameter_list):
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to register function {} in no scope ".format(name))
        functions_in_top_smbltab = self.symbol_table[self.current_scope_index - 1]["subprogram"]
        functions_in_top_smbltab[name] = FunctionSymbol(name, header, None, parameter_list)

    def declare_func(self, name, tokens):
        self.symbol_table[self.current_scope_index - 1]["subprogram"][name].tokens = tokens

    def register_value(self, name, value_type, mutable, value = None):
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to register value {} in no scope ".format(name))
        values_in_top_smbltab = self.symbol_table[self.current_scope_index]["value"]
        values_in_top_smbltab[name] = ValueSymbol(name, value_type, mutable, value)

    def register_array(self, name, array_type, periods):  # periods(start, last) : [[1, 5], [2, 4]]
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to register array {} in no scope ".format(name))
        arrays_in_top_smbltab = self.symbol_table[self.current_scope_index]["array"]
        dimensions = []
        for dimension in periods:
            dimensions.append([dimension[1] - dimension[0] + 1, dimension[0]])
        arrays_in_top_smbltab[name] = ArraySymbol(name, array_type,
                                                  dimensions)  # dimensions(length, start) : [[5, 1], [3, 2]]

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

    def get_value(self, name):
        value_symbol = self.get_values().get(name)
        context_index = self.current_scope_index
        while value_symbol is None and context_index >= 0:
            value_symbol = self.symbol_table[context_index]["value"].get(name)
            context_index -= 1
        return value_symbol

    def get_array(self, name):
        array_symbol = self.get_arrays().get(name)
        context_index = self.current_scope_index
        while array_symbol is None and context_index >= 0:
            array_symbol = self.symbol_table[context_index]["array"].get(name)
            context_index -= 1
        return array_symbol

    def get_func(self, name):
        index = self.current_scope_index
        func = None
        while func is None and index >= 0:
            func = self.symbol_table[index]["subprogram"].get(name)
            index -= 1
        return func

    def record_error(self, message):
        self.on_error = True
        self.error_messages.append(message)

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
    def __init__(self, name, header, tokens, parameter_list):
        self.name = name
        self.header = header
        self.tokens = tokens
        self.parameter_list = parameter_list

    def __repr__(self) -> str:
        description = "Function: " + self.name + "\n"
        description += "Header: " + " ".join(self.header) + "\n"
        description += "Tokens: " + str(self.tokens) + "\n"
        description += "Parameters: " + str(self.parameter_list) + "\n"
        return description


class ValueSymbol:
    def __init__(self, name, value_type, mutable, value):
        self.name = name
        self.type = value_type
        self.mutable = mutable
        self.value = value

    def __repr__(self) -> str:
        description = "Value: " + self.name + "\n"
        description += "Type: " + self.type + "\n"
        description += "Mutable: " + str(self.mutable) + "\n"
        description += "Value: " + str(self.value) + "\n"
        return description


class ArraySymbol:
    def __init__(self, name, array_type, dimensions):
        self.name = name
        self.type = array_type
        self.dimensions = dimensions  # [[length1, start1], [length2, start2]...]
        length_sum = 0
        for dimension in self.dimensions:
            length_sum += dimension[0]
        self.value = [None] * length_sum

    def __repr__(self) -> str:
        description = "Array: " + self.name + "\n"
        description += "Type: " + self.type + "\n"
        description += "Dimensions: " + str(self.dimensions) + "\n"
        description += "Value: " + str(self.value) + "\n"
        return description
