# LL(1) might be the easiest place to start (i.e. recursive descent)
# This document outlines LL(1) parsers (and limitations of LL(1) grammars) nicely:
# http://web.stanford.edu/class/archive/cs/cs143/cs143.1128/handouts/090%20Top-Down%20Parsing.pdf

# Note that that document gives a mechanism for determining if a grammar is LL(1), which I should implement as
# a check here

from collections import namedtuple

Rule = namedtuple('Rule', ['sym', 'exp'])
TSym = namedtuple('TerminalSymbol', 'char')
NSym = namedtuple('NonterminalSymbol', 'char')

EPSILON_CHAR = ''

# T' -> G, E' -> H as defined in the stanford recitation notes
# This is a grammar for addition or multiplication strings with only 0s (obviously nonsensical)
# NOTE - just for testing!
test_rules = [
    Rule(NSym('E'), [NSym('T'), NSym('H')]),

    Rule(NSym('H'), [TSym('+'), NSym('T'), NSym('H')]),
    Rule(NSym('H'), [TSym('')]),

    Rule(NSym('T'), [NSym('F'), NSym('G')]),

    Rule(NSym('G'), [TSym('*'), NSym('F'), NSym('G')]),
    Rule(NSym('G'), [TSym('')]),

    Rule(NSym('F'), [TSym('('), NSym('E'), TSym(')')]),
    Rule(NSym('F'), [TSym('0')])
]

# Output is a map of (nonterminal_char, terminal_char) -> Rule
def build_parse_table(rules):
    first_sets = build_first_sets(rules)
    # TODO
    #follow_sets = build_follow_sets(rules)

    # Build parse table from first/follow sets. If any duplicate vals for a single tuple key, raise an
    # exception stating that the grammar isn't LL(1)
    return {}

def build_first_sets(rules):
    first_sets = {}
    nonterm_syms = set([rule.sym for rule in rules])

    for sym in nonterm_syms:
        if sym not in first_sets:
            first_sets = _add_sym_to_first_sets(sym, rules, first_sets)

    return first_sets

def _add_sym_to_first_sets(sym, rules, first_sets):
    sym_rules = [rule for rule in rules if rule.sym == sym]
    sym_first_sets = set()

    for rule in sym_rules:
        i = 0
        found_epsilon = True
        while found_epsilon and i < len(rule.exp):
            next_sym = rule.exp[i]
            found_epsilon = False

            if type(next_sym) is TSym:
                sym_first_sets.add(next_sym.char)

            else:
                if next_sym.char not in first_sets:
                    first_sets = _add_sym_to_first_sets(next_sym, rules, first_sets)

                next_terms = first_sets[next_sym.char]
                if EPSILON_CHAR in next_terms:
                    found_epsilon = True
                    to_add = next_terms.copy()
                    to_add.remove(EPSILON_CHAR)

                    sym_first_sets |= to_add

                else:
                    to_add = next_terms.copy()

                    sym_first_sets |= to_add
            i += 1

        if found_epsilon and i is len(rule.exp) and len(sym_first_sets) is 0:
            sym_first_sets.add(EPSILON_CHAR)

    first_sets[sym.char] = sym_first_sets
    return first_sets


class LLParser:
    # We may want to add some helpers for converting a string to rules, etc.
    # Assume that the first rule supplied is the start rule
    def __init__(self, rules):
        # TODO add some basic rule validation
        # - no nonterminal symbols used without
        # TODO add some grammar transformation (remove left recursion, left factoring)
        self.start_symbol = rules[0].sym
        self.parse_table = self.build_parse_table(rules)
