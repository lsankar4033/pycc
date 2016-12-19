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

        self.assertEqual(remove_left_recursion(grammar.rules),
                         build_grammar([('A', 'b')]).rules)

    def test_leave_nonrecursive_rules(self):
        grammar = build_grammar(
            [('A', 'b'),
             ('A', 'B'),
             ('B', 'c')])

        self.assertEqual(remove_left_recursion(grammar.rules),
                         grammar.rules)

    def test_single_direct_recursion(self):
        grammar = build_grammar(
            [('A', 'Ab')])

        self.assertEqual(remove_left_recursion(grammar.rules),
                         build_grammar(
                             [('A', 'B'),
                              ('B', 'bB')]).rules)

        grammar = build_grammar(
            [('A', 'Ab'),
             ('A', 'c')])

        self.assertEqual(remove_left_recursion(grammar.rules),
                         build_grammar(
                             [('A', 'cB'),
                              ('B', 'bB'),
                              ('B', EPSILON_CHAR)]).rules)

    # TODO - add test for indirect recursion removal
