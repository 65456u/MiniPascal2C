class Context:
    def __init__(self):
        self.functions = {}
        self.current_scope = None

    def register_func(self, name,header,tokens):
        the_function=MiniPascalFunction(name,header,tokens)
        self.functions[name]=the_function
    
    def get_funcs(self):
        return self.functions



class MiniPascalFunction:
    def __init__(self, name, header, tokens):
        self.name = name
        self.header = header
        self.tokens = tokens
