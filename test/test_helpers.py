from pycc.grammar import *
from pycc.constants import *

def build_grammar(rule_strs):
    """Test-only helper for building Grammar object from an array of the form:
    [ ('A', 'Bc'),
      ('B', 'd'),
      ('B', '') ]

    Note that this assumes that nonterminals are identified by their existence on the left-hand side of a
    rule, so terminals with the same defining char as nonterminals are not allowed. Additionally, we assume
    that no 'epsilon' char can occur within an expression (as this would make for an invalid grammar).
    """
    nonterm_chars = set([r[0] for r in rule_strs])

    start_symbol = NSym(rule_strs[0][0])

    rules = []
    for sym, exp_str in rule_strs:
        exp_chars = list(exp_str)

        if len(exp_chars) is 0:
            exp = [TSym('')]
        else:
            exp = list(map(lambda c: NSym(c) if c in nonterm_chars else TSym(c), exp_chars))

        rules.append(Rule(NSym(sym), exp))

    return Grammar(rules, start_symbol)

# E' -> H, T' -> G
# Represents a +,* string with 0s
integration_test_grammar = build_grammar(
    [('E', 'TH'),
     ('H', '+TH'),
     ('H', EPSILON_CHAR),
     ('T', 'FG'),
     ('G', '*FG'),
     ('G', EPSILON_CHAR),
     ('F', '(E)'),
     ('F', '0')])

# Regex grammar for regexes with only '*', concat, '|', and parens
# TODO add special characters to grammar parsing so we can do better than just parsing regexes with a single
# character.
# TODO write LR parser to test this guy
regex_grammar = build_grammar(
    [('R', 'D'),

     ('P', '(R)'),

     ('D', 'C'),
     ('D', 'C|D'),
     ('D', 'P'),
     ('D', 'P|D'),

     ('C', 'S'),
     ('C', 'SC'),
     ('C', 'P'),
     ('C', 'PC'),

     ('S', 'A'),
     ('S', 'A*'),
     ('S', 'P'),
     ('S', 'P*')])

def rules_str(rules):
    return str([str(r) for r in rules])
