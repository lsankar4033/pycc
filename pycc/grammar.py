class Rule:
    def __init__(self, sym, exp_syms):
        self.sym = sym
        self.exp_syms = exp_syms

    def __str__(self):
        return '{} -> {}'.format(str(self.sym), "".join([str(e) for e in self.exp_syms]))

class TSym:
    def __init__(self, char):
        self.char = char

    def __str__(self):
        return self.char

class NSym:
    def __init__(self, char):
        self.char = char

    def __str__(self):
        return self.char
