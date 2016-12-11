# LL(1) might be the easiest place to start (i.e. recursive descent)
# This document outlines LL(1) parsers (and limitations of LL(1) grammars) nicely:
# http://web.stanford.edu/class/archive/cs/cs143/cs143.1128/handouts/090%20Top-Down%20Parsing.pdf

# Note that that document gives a mechanism for determining if a grammar is LL(1), which I should implement as
# a check here

from collections import namedtuple

# TODO - It's a little unfortunate that we need to translate between symbol and char space while building
# first/follow sets. There may be a cleaner way to do this.
Rule = namedtuple('Rule', ['sym', 'exp_syms'])
TSym = namedtuple('TerminalSymbol', 'char')
NSym = namedtuple('NonterminalSymbol', 'char')

EPSILON_CHAR = ''
END_SYMBOL = 'EOF'

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
    follow_sets = build_follow_sets(rules, first_sets)

    # Build parse table from first/follow sets. If any duplicate vals for a single tuple key, raise an
    # exception stating that the grammar isn't LL(1)
    return {}

def build_first_sets(rules):
    first_sets = {}
    nonterm_syms = set([rule.sym for rule in rules])

    for sym in nonterm_syms:
        if sym.char not in first_sets:
            first_sets = _add_sym_to_first_sets(sym, rules, first_sets)

    return first_sets

def _add_sym_to_first_sets(sym, rules, first_sets):
    sym_rules = [rule for rule in rules if rule.sym == sym]
    sym_first_sets = set()

    for rule in sym_rules:
        i = 0
        has_trailing_epsilon = True
        while has_trailing_epsilon and i < len(rule.exp_syms):
            next_sym = rule.exp_syms[i]
            has_trailing_epsilon = False

            # NOTE this assumes that there aren't terminal epsilons in the middle of expressions. I should
            # check this during grammar validation
            if type(next_sym) is TSym:
                sym_first_sets.add(next_sym.char)

            else:
                if next_sym.char not in first_sets:
                    first_sets = _add_sym_to_first_sets(next_sym, rules, first_sets)

                next_terms = first_sets[next_sym.char]
                if EPSILON_CHAR in next_terms:
                    has_trailing_epsilon = True
                    to_add = next_terms.copy()
                    to_add.remove(EPSILON_CHAR)

                    sym_first_sets |= to_add

                else:
                    to_add = next_terms.copy()

                    sym_first_sets |= to_add
            i += 1

        if has_trailing_epsilon and i is len(rule.exp_syms) and len(sym_first_sets) is 0:
            sym_first_sets.add(EPSILON_CHAR)

    first_sets[sym.char] = sym_first_sets
    return first_sets

# NOTE - assumes start rule is first rule in 'rules'
def build_follow_sets(rules, first_sets):
    start_sym = rules[0].sym
    follow_sets = {start_sym.char: set([END_SYMBOL])}
    nonterm_syms = set([rule.sym for rule in rules])

    for sym in nonterm_syms:
        if sym is start_sym or sym.char not in follow_sets:
            follow_sets = _add_sym_to_follow_sets(sym, rules, first_sets, follow_sets)

    return follow_sets

# TODO - much of the logic in this method is duplicated in first_set computation...
def _add_sym_to_follow_sets(sym, rules, first_sets, follow_sets):
    sym_follow_sets = follow_sets[sym.char] if sym.char in follow_sets else set()
    rules_with_sym = [rule for rule in rules if sym in rule.exp_syms]
    for rule in rules_with_sym:
        sym_ind = rule.exp_syms.index(sym)

        if sym_ind is len(rule.exp_syms) - 1:
            if rule.sym.char not in follow_sets:
                follow_sets = _add_sym_to_follow_sets(rule.sym, rules, first_sets, follow_sets)

            sym_follow_sets |= follow_sets[rule.sym.char]

        else:
            i = sym_ind + 1
            has_trailing_epsilon = True
            while has_trailing_epsilon and i < len(rule.exp_syms):
                has_trailing_epsilon = False
                next_sym = rule.exp_syms[i]

                if type(next_sym) is TSym:
                    sym_follow_sets.add(next_sym.char)

                else:
                    next_terms = first_sets[next_sym.char]
                    if EPSILON_CHAR in next_terms:
                        has_trailing_epsilon = True
                        to_add = next_terms.copy()
                        to_add.remove(EPSILON_CHAR)

                        sym_follow_sets |= to_add

                    else:
                        to_add = next_terms.copy()

                        sym_follow_sets |= to_add

                i += 1

            if has_trailing_epsilon and i is len(rule.exp_syms) and len(sym_follow_sets) is 0:
                # TODO - this code is duplicated above
                if rule.sym.char not in follow_sets:
                    follow_sets = _add_sym_to_follow_sets(rule.sym, rules, first_sets, follow_sets)

                sym_follow_sets |= follow_sets[rule.sym.char]

    follow_sets[sym.char] = sym_follow_sets
    return follow_sets


class LLParser:
    # We may want to add some helpers for converting a string to rules, etc.
    # Assume that the first rule supplied is the start rule
    def __init__(self, rules):
        # TODO add some basic rule validation
        # - no nonterminal symbols used without
        # TODO add some grammar transformation (remove left recursion, left factoring)
        self.start_symbol = rules[0].sym
        self.parse_table = build_parse_table(rules)
