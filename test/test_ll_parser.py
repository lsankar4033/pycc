import unittest
from pycc.ll_parser import *
from pycc.grammar import *

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

def _build_follow_sets(rule_strs, first_sets):
    rules = build_rules(rule_strs)
    return build_follow_sets(rules, first_sets)

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
        rule_strs = [
            ('A', 'b')
        ]
        first_sets = {
            'A': set(['b'])
        }
        follow_sets = _build_follow_sets(rule_strs, first_sets)
        self.assertIn(END_SYMBOL, follow_sets['A'])

    def test_basic(self):
        rule_strs = [
            ('A', 'Bc'),
            ('B', 'b')
        ]
        first_sets = {
            'A': set(['b']),
            'B': set(['b'])
        }
        follow_sets = _build_follow_sets(rule_strs, first_sets)
        self.assertEqual(follow_sets['B'], set(['c']))

    def test_epsilon(self):
        rule_strs = [
            ('A', 'BCD'),
            ('B', 'b'),
            ('C', EPSILON_CHAR),
            ('D', 'd')
        ]
        first_sets = {
            'A': set(['b']),
            'B': set(['b']),
            'C': set([EPSILON_CHAR]),
            'D': set(['d'])
        }
        follow_sets = _build_follow_sets(rule_strs, first_sets)
        self.assertEqual(follow_sets['B'], set(['d']))

        rule_strs = [
            ('A', 'Be'),
            ('B', 'CDE'),
            ('C', 'c'),
            ('D', EPSILON_CHAR),
            ('E', EPSILON_CHAR)
        ]
        first_sets = {
            'A': set(['c']),
            'B': set(['c']),
            'C': set(['c']),
            'D': set([EPSILON_CHAR]),
            'E': set([EPSILON_CHAR])
        }
        follow_sets = _build_follow_sets(rule_strs, first_sets)
        self.assertEqual(follow_sets['C'], set(['e']))

integration_test_rules = build_rules(
    [
        ('E', 'TH'),
        ('H', '+TH'),
        ('H', EPSILON_CHAR),
        ('T', 'FG'),
        ('G', '*FG'),
        ('G', EPSILON_CHAR),
        ('F', '(E)'),
        ('F', '0')
    ])

class TestTopoSort(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(topo_sort({'A': set(['B']), 'B': set(['C'])}),
                         ['A', 'B', 'C'])

    def test_multiple_dependency(self):
        ts = topo_sort({'A': set(['B']), 'C': set(['B'])})
        self.assertTrue(ts.index('A') < ts.index('B'))
        self.assertTrue(ts.index('C') < ts.index('B'))

    def test_cyclic_dependency(self):
        with self.assertRaises(ValueError):
            topo_sort({'A': set(['B']), 'B': set(['A'])})

# A series of integration tests run on a more complex sample grammar
class TestIntegration(unittest.TestCase):
    def test_first_sets(self):
        first_sets = build_first_sets(integration_test_rules)
        self.assertEqual(first_sets, {
            'E': set(['(', '0']),
            'T': set(['(', '0']),
            'F': set(['(', '0']),
            'G': set(['*', EPSILON_CHAR]),
            'H': set(['+', EPSILON_CHAR])})

    def test_follow_sets(self):
        first_sets = build_first_sets(integration_test_rules)
        follow_sets = build_follow_sets(integration_test_rules, first_sets)

        self.assertEqual(follow_sets, {
            'E': set([END_SYMBOL, ')']),
            'H': set([END_SYMBOL, ')']),
            'T': set(['+', END_SYMBOL, ')']),
            'G': set(['+', END_SYMBOL, ')']),
            'F': set(['*', '+', END_SYMBOL, ')'])})
