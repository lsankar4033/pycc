# TODO - switch back to namedtuple and add 'str' helper methods
# A good route may be to define a 'Rules' class that has a bunch of named tuples and a string method on itself
# for easy testing
from collections import namedtuple

class Grammar:
    # TODO - grammar validation
    def __init__(self, rules, start_symbol):
        self.rules = rules
        self.start_symbol = start_symbol

    def stringify_rules(self):
        rule_str = ""

        for rule in self.rules:
            exp_sym_strs = [sym.char for sym in rule.exp_syms]
            rule_str = rule_str + rule.sym.char + " -> " + str(exp_sym_strs) + "\n"

        return rule_str.strip()

    def __str__(self):
        start_sym_str = "start symbol: {}".format(self.start_symbol.char)
        rules_str = "rules: \n{}".format(self.stringify_rules())

        return start_sym_str + "\n" + rules_str

    def __eq__(self, other):
        return self.start_symbol == other.start_symbol and self.rules == other.rules

# Expression symbol is a list of symbols
Rule = namedtuple('Rule', 'sym exp_syms')

# Terminal symbol
TSym = namedtuple('TSym', 'char')

# Nonterminal symbol
NSym = namedtuple('NSym', 'char')
