def rules_str(rules):
    return str([str(r) for r in rules])

class Rule:
    def __init__(self, sym, exp_syms):
        self.sym = sym
        self.exp_syms = exp_syms

    def __str__(self):
        return '{} -> {}'.format(str(self.sym), "".join([str(e) for e in self.exp_syms]))

class Sym:
    def __init__(self, char):
        self.char = char

    def __hash__(self):
        return hash(self.char)

    def __eq__(self, other):
        return self.char == other.char

    def __str__(self):
        return self.char

class TSym(Sym):
    pass

class NSym(Sym):
    pass
