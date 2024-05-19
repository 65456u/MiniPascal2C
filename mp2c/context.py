from collections import deque


class Context:
    def __init__(self):
        """
        Initializes a new instance of the Context class.
        
        The Context class is responsible for managing the symbol table and error handling.
        
        Attributes:
        - current_scope_index: An integer representing the index of the current scope in the symbol table.
        - symbol_table: A deque representing the symbol table.
        - on_error: A boolean indicating whether an error has occurred.
        - error_messages: A list of error messages.
        """
        self.current_scope_index = -1
        self.symbol_table = deque()
        self.on_error = False
        self.error_messages = []

    def enter_scope(self):
        """
        Enter a new scope in the symbol table.

        This method appends a new dictionary to the symbol table, representing a new scope.
        The new scope is initially empty, with separate dictionaries for values, arrays, and subprograms.

        """
        self.symbol_table.append({"value": {}, "array": {}, "subprogram": {}})
        self.current_scope_index += 1

    def exit_scope(self):
        """
        Exit the current scope by removing it from the symbol table and updating the current scope index.
        """
        self.symbol_table.pop()
        self.current_scope_index -= 1

    def register_func(self, name, header, parameter_list, var_parameter, tokens = None, is_library = False):
        """
        Register a function in the symbol table.

        Args:
            name (str): The name of the function.
            header (list): The header of the function.
            parameter_list (list): The list of parameters of the function.
            var_parameter (list): A list indicating whether each parameter is a variable parameter.
            tokens (list, optional): The tokens associated with the function. Defaults to None.
            is_library (bool, optional): Indicates if the function is a library function. Defaults to False.

        Raises:
            Exception: If the current scope index is invalid.

        """
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to register function {} in no scope ".format(name))
        functions_in_top_smbltab = self.symbol_table[self.current_scope_index - 1]["subprogram"]
        functions_in_top_smbltab[name] = FunctionSymbol(name, header, tokens, parameter_list, var_parameter, is_library)

    def declare_func(self, name, tokens):
        """
        Declare a function in the symbol table.

        Args:
            name (str): The name of the function.
            tokens (list): The tokens representing the function.

        Returns:
            None
        """
        self.symbol_table[self.current_scope_index - 1]["subprogram"][name].tokens = tokens

    def register_value(self, name, value_type, mutable, value = None, var = False):
        """Register a value in the symbol table.

        Args:
            name (str): The name of the value.
            value_type (str): The type of the value.
            mutable (bool): Indicates whether the value is mutable or not.
            value (Any, optional): The initial value of the variable. Defaults to None.
            var (bool, optional): Indicates whether the value is a variable or not. Defaults to False.

        Raises:
            Exception: If the current scope index is out of range.

        """
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("Try to register value {} in no scope".format(name))
        values_in_top_smbltab = self.symbol_table[self.current_scope_index]["value"]
        values_in_top_smbltab[name] = ValueSymbol(name, value_type, mutable, value, var)

    def register_array(self, name, array_type, periods):
        """
        Register an array in the symbol table.
        Parameters:
        - name (str): The name of the array.
        - array_type (str): The type of the array.
        - periods (list): The periods of the array.
        Raises:
        - Exception: If the current scope index is out of range.
        Returns:
        - None
        """
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to register array {} in no scope ".format(name))
        arrays_in_top_smbltab = self.symbol_table[self.current_scope_index]["array"]
        dimensions = []
        for dimension in periods:
            dimensions.append([dimension[1] - dimension[0] + 1, dimension[0]])
        arrays_in_top_smbltab[name] = ArraySymbol(name, array_type,
                                                  dimensions)

    def get_funcs(self):
        """
        Returns the list of functions in the current scope.

        Raises:
            Exception: If the current scope index is out of range.

        Returns:
            list: The list of functions in the current scope.
        """
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to get functions in no scope ")
        return self.symbol_table[self.current_scope_index]["subprogram"]

    def get_values(self):
        """
        Returns the values stored in the current scope of the symbol table.

        Raises:
            Exception: If the current scope index is out of range.

        Returns:
            dict: The values stored in the current scope.
        """
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to get values in no scope")
        return self.symbol_table[self.current_scope_index]["value"]

    def get_arrays(self):
        """
        Get the arrays defined in the current scope.

        Returns:
            dict: The arrays defined in the current scope.

        Raises:
            Exception: If the current scope index is out of range.
        """
        if self.current_scope_index < 0 or self.current_scope_index >= len(self.symbol_table):
            raise Exception("try to get arrays in no scope ")
        return self.symbol_table[self.current_scope_index]["array"]

    def get_value(self, name):
        """
        Retrieves the value associated with the given name from the symbol table.

        Args:
            name (str): The name of the value to retrieve.

        Returns:
            Any: The value associated with the given name, or None if the name is not found.
        """
        value_symbol = self.get_values().get(name)
        context_index = self.current_scope_index
        while value_symbol is None and context_index >= 0:
            value_symbol = self.symbol_table[context_index]["value"].get(name)
            context_index -= 1
        return value_symbol

    def get_array(self, name):
        """
        Retrieves the array symbol with the given name from the symbol table.

        Args:
            name (str): The name of the array symbol to retrieve.

        Returns:
            dict or None: The array symbol if found, None otherwise.
        """
        array_symbol = self.get_arrays().get(name)
        context_index = self.current_scope_index
        while array_symbol is None and context_index >= 0:
            array_symbol = self.symbol_table[context_index]["array"].get(name)
            context_index -= 1
        return array_symbol

    def get_func(self, name):
        """
        Retrieves a function from the symbol table by its name.

        Args:
            name (str): The name of the function to retrieve.

        Returns:
            func (object): The function object if found, None otherwise.
        """
        index = self.current_scope_index
        func = None
        while func is None and index >= 0:
            func = self.symbol_table[index]["subprogram"].get(name)
            index -= 1
        return func

    def record_error(self, message):
        """
        Records an error message and sets the `on_error` flag to True.
        
        Args:
            message (str): The error message to be recorded.
        """
        self.on_error = True
        self.error_messages.append(message)

    def declare_library_functions(self):
        """
        Declares and registers library functions.

        This method declares and registers various single and double math functions as library functions.
        The function names and their corresponding signatures are provided in the `single_double_math_function_names` list.
        Each function is registered with its signature, input parameter types, and other relevant information.

        Args:
            self: The current instance of the class.

        Returns:
            None
        """
        single_double_math_function_names = ["acos", "asin", "atan", "cos", "cosh", "sin", "sinh", "tanh", "exp", "log",
                                             "log10", "sqrt", "ceil", "fabs", "floor"]
        for function_name in single_double_math_function_names:
            self.register_func(function_name, ["float", function_name, "(", "float", "x", ")", ";"],
                               [{'ids': ['x'], 'type': 'float'}], [False], tokens = [], is_library = True)


class FunctionSymbol:
    """
    Represents a function symbol in the MiniPascal to C compiler.

    Attributes:
        name (str): The name of the function.
        header (list): The header of the function.
        tokens (list): The tokens associated with the function.
        parameter_list (list): The list of parameters for the function.
        var_parameter (bool): Indicates if the function has a variable parameter.
        is_library (bool): Indicates if the function is a library function.

    Methods:
        __repr__(): Returns a string representation of the FunctionSymbol object.
    """

    def __init__(self, name, header, tokens, parameter_list, var_parameter, is_library = False):
        self.name = name
        self.header = header
        self.tokens = tokens
        self.parameter_list = parameter_list
        self.var_parameter = var_parameter
        self.is_library = is_library


class ValueSymbol:
    """
    Represents a symbol that holds a value in the context.

    Attributes:
        name (str): The name of the value symbol.
        type (str): The type of the value.
        mutable (bool): Indicates whether the value is mutable or not.
        value: The actual value.
        var (bool): Indicates whether the symbol is a variable or not.
    """

    def __init__(self, name, value_type, mutable, value, var = False):
        self.name = name
        self.type = value_type
        self.mutable = mutable
        self.value = value
        self.var = var


class ArraySymbol:
    """
    Represents an array symbol in the MiniPascal to C compiler.

    Attributes:
        name (str): The name of the array symbol.
        type (str): The type of the array symbol.
        dimensions (list): The dimensions of the array symbol.
        value (list): The value of the array symbol.
    """

    def __init__(self, name, array_type, dimensions):
        self.name = name
        self.type = array_type
        self.dimensions = dimensions  # [[length1, start1], [length2, start2]...]
        length_sum = 0
        for dimension in self.dimensions:
            length_sum += dimension[0]
        self.value = [None] * length_sum
