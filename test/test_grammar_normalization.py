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
        rules = build_rules(
            [('A', 'A'),
             ('A', 'b')])

        self.assertEqual(remove_left_recursion(rules),
                         build_rules([('A', 'b')]))

    def test_leave_nonrecursive_rules(self):
        rules = build_rules(
            [('A', 'b'),
             ('A', 'B'),
             ('B', 'c')])

        self.assertEqual(remove_left_recursion(rules),
                         rules)

    def test_single_direct_recursion(self):
        rules = build_rules(
            [('A', 'Ab')])

        self.assertEqual(remove_left_recursion(rules),
                         build_rules(
                             [('A', 'B'),
                              ('B', 'bB')]))

        rules = build_rules(
            [('A', 'Ab'),
             ('A', 'c')])

        self.assertEqual(remove_left_recursion(rules),
                         build_rules(
                             [('A', 'cB'),
                              ('B', 'bB'),
                              ('B', EPSILON_CHAR)]))

    # TODO - add test for indirect recursion removal
