import unittest
from pycc.ll_parser import *

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

def _build_first_sets(rule_strs):
    rules = build_rules(rule_strs)
    return build_first_sets(rules)

class TestFirstSets(unittest.TestCase):
    def test_basic(self):
        first_sets = _build_first_sets([
            ('A', 'ab')
        ])
        self.assertEqual(first_sets['A'], set(['a']))

    def test_child_inheritance(self):
        first_sets = _build_first_sets([
            ('A', 'B'),
            ('B', 'b')
        ])
        self.assertEqual(first_sets['A'], set(['b']))

    def test_child_epsilon(self):
        first_sets = _build_first_sets([
            ('A', 'B'),
            ('B', EPSILON_CHAR),
            ('B', 'b')
        ])
        self.assertEqual(first_sets['A'], set(['b']))
        self.assertEqual(first_sets['B'], set(['b', EPSILON_CHAR]))

        first_sets = _build_first_sets([
            ('A', 'BC'),
            ('B', EPSILON_CHAR),
            ('B', 'b'),
            ('C', 'c')
        ])
        self.assertEqual(first_sets['A'], set(['b', 'c']))

        first_sets = _build_first_sets([
            ('A', 'BC'),
            ('B', EPSILON_CHAR),
            ('C', EPSILON_CHAR)
        ])
        self.assertEqual(first_sets['A'], set([EPSILON_CHAR]))

class TestFollowSets(unittest.TestCase):

    def test_eof_follows_start(self):
        # A -> a

        pass
