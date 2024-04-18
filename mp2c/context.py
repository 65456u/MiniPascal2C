class Context:
    def __init__(self):
        self.functions = {}

    def register_func(self, name):
        self.functions[name] = None

    def declare_function(self, name, tokens):
        self.functions[name] = tokens
