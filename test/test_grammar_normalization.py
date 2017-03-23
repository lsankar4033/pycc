import unittest
from pycc.grammar_normalization import *
from test.test_helpers import *

def generate_next_sym(start_sym):
    i = ord(start_sym)
    while True:
        i += 1
        yield chr(i)

class TestRemoveLeftRecursion(unittest.TestCase):
    def test_remove_trivial_rules(self):
        grammar = build_grammar(
            [('A', 'A'),
             ('A', 'b')])

        self.assertEqual(remove_left_recursion(grammar),
                         build_grammar([('A', 'b')]))

    def test_leave_nonrecursive_rules(self):
        grammar = build_grammar(
            [('A', 'b'),
             ('A', 'B'),
             ('B', 'c')])

        self.assertEqual(remove_left_recursion(grammar),
                         grammar)

    def test_single_direct_recursion(self):
        grammar = build_grammar(
            [('A', 'Ab')])

        self.assertEqual(remove_left_recursion(grammar),
                         build_grammar(
                             [('A', 'B'),
                              ('B', 'bB')]))

        grammar = build_grammar(
            [('A', 'Ab'),
             ('A', 'c')])

        self.assertEqual(remove_left_recursion(grammar),
                         build_grammar(
                             [('A', 'cB'),
                              ('B', 'bB'),
                              ('B', EPSILON_CHAR)]))

class TestLeftFactor(unittest.TestCase):
    def test_no_common_left_factors(self):
        grammar = build_grammar(
            [('A', 'b'),
             ('A', 'c')])

        self.assertEqual(left_factor(grammar), grammar)

    def test_single_common_left_factor(self):
        grammar = build_grammar(
            [('A', 'bc'),
             ('A', 'bd')])

        self.assertEqual(left_factor(grammar),
                         build_grammar(
                             [('A', 'bB'),
                              ('B', 'c'),
                              ('B', 'd')]))

    def test_nested_common_left_factor(self):
        grammar = build_grammar(
            [('A', 'bc'),
             ('A', 'bd'),
             ('A', 'bce'),
             ('A', 'bcf')])

        self.assertEqual(left_factor(grammar),
                         build_grammar(
                             [('A', 'bcB'),
                              ('B', EPSILON_CHAR),
                              ('B', 'e'),
                              ('B', 'f'),
                              ('A', 'bd')]))
