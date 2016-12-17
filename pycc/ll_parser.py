import pycc.parse_table as parse_table
from pycc.constants import EPSILON_CHAR, END_SYMBOL

# TODO - docstring
class LLParser:
    # We may want to add some helpers for converting a string to rules, etc.
    # Assume that the first rule supplied is the start rule
    def __init__(self, rules):
        # TODO add some basic rule validation
        # - no nonterminal symbols used without
        # TODO add some grammar transformation (remove left recursion, left factoring)
        # TODO add the ability for escape characters (like \s or \w) in grammars
        self.start_symbol = rules[0].sym.char
        self.nonterminals = set([rule.sym.char for rule in rules])

        # TODO - it might be worth consolidating this into one method call in the future
        first_sets = parse_table.build_first_sets(rules)
        follow_sets = parse_table.build_follow_sets(rules, first_sets)
        self.parse_table = parse_table.build_parse_table(rules, first_sets, follow_sets)

    def parse(self, s):
        parse_stack = [END_SYMBOL, self.start_symbol]
        i = 0

        s_list = list(s) + [END_SYMBOL]
        while i < len(s_list):

            # successful full match
            if parse_stack[-1] == END_SYMBOL and s_list[i] == END_SYMBOL:
                return True

            # match
            elif parse_stack[-1] == s_list[i]:
                parse_stack.pop()
                i += 1

            # predict attempt
            elif parse_stack[-1] != s_list[i] and parse_stack[-1] in self.nonterminals:
                X = parse_stack.pop()
                a = s_list[i]

                # predict miss
                if (X, a) not in self.parse_table:
                    return False

                syms = self.parse_table[(X, a)].copy()
                syms.reverse()

                parse_stack = parse_stack + [sym for sym in syms if sym is not EPSILON_CHAR]

            # mismatch
            else:
                return False

        return True
