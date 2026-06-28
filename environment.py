class Env:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
        self.current_return = parent.current_return if parent else None

    def resolve(self, name):
        if name in self.vars:
            return self
        if self.parent:
            return self.parent.resolve(name)
        return None

    def lookup(self, name):
        target_env = self.resolve(name)
        if target_env:
            return target_env.vars[name]
        return None