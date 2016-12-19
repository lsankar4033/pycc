# TODO - switch back to namedtuple and add 'str' helper methods
# A good route may be to define a 'Rules' class that has a bunch of named tuples and a string method on itself
# for easy testing

class Rule:
    def __init__(self, sym, exp_syms):
        self.sym = sym
        self.exp_syms = exp_syms

    def __str__(self):
        return '{} -> {}'.format(str(self.sym), "".join([str(e) for e in self.exp_syms]))

    def __eq__(self, other):
        return self.sym == other.sym and self.exp_syms == other.exp_syms

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
