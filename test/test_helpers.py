from pycc.grammar import *
from pycc.constants import *

def build_rules(rule_strs):
    """Test-only helper for building rule array from an array of the form:
    [ ('A', 'Bc'),
      ('B', 'd'),
      ('B', '') ]

    Note that this assumes that nonterminals are identified by their existence on the left-hand side of a
    rule, so terminals with the same defining char as nonterminals are not allowed. Additionally, we assume
    that no 'epsilon' char can occur within an expression (as this would make for an invalid grammar).
    """
    nonterm_chars = set([r[0] for r in rule_strs])

    rules = []
    for sym, exp_str in rule_strs:
        exp_chars = list(exp_str)

        if len(exp_chars) is 0:
            exp = [TSym('')]
        else:
            exp = list(map(lambda c: NSym(c) if c in nonterm_chars else TSym(c), exp_chars))

        rules.append(Rule(NSym(sym), exp))

    return rules

# E' -> H, T' -> G
# Represents a +,* string with 0s
integration_test_rules = build_rules(
    [('E', 'TH'),
     ('H', '+TH'),
     ('H', EPSILON_CHAR),
     ('T', 'FG'),
     ('G', '*FG'),
     ('G', EPSILON_CHAR),
     ('F', '(E)'),
     ('F', '0')])

def rules_str(rules):
    return str([str(r) for r in rules])
