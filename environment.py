class Env:
    def __init__(self, parent=None):
        self.vars = {}
        self.funcs = {}
        self.parent = parent
        self.current_return = parent.current_return if parent else None

    def lookup_var(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.lookup_var(name)
        return None

    def lookup_func(self, name):
        if name in self.funcs:
            return self.funcs[name]
        if self.parent:
            return self.parent.lookup_func(name)
        return None