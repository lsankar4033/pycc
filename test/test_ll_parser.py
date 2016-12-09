import unittest
from pycc.ll_parser import *

class TestFirstSets(unittest.TestCase):
    def test_basic(self):
        # A -> ab
        rules = [Rule(NSym('A'), [TSym('a'), TSym('b')])]
        self.assertEqual(build_first_sets(rules), {'A': set(['a'])})

    def test_child_inheritance(self):
        # A -> B
        # B -> b
        rules = [
            Rule(NSym('A'), [NSym('B')]),
            Rule(NSym('B'), [TSym('b')])
        ]
        self.assertEqual(build_first_sets(rules),
                         {
                             'A': set(['b']),
                             'B': set(['b'])
                         })

    def test_child_epsilon(self):
        # A -> B
        # B -> epsilon | b
        rules = [
            Rule(NSym('A'), [NSym('B')]),
            Rule(NSym('B'), [TSym(EPSILON_CHAR)]),
            Rule(NSym('B'), [TSym('b')])
        ]

        self.assertEqual(build_first_sets(rules),
                         {
                             'A': set(['b']),
                             'B': set(['b', EPSILON_CHAR])
                         })

        # A -> BC
        # B -> epsilon
        # C -> c
        rules = [
            Rule(NSym('A'), [NSym('B'), NSym('C')]),
            Rule(NSym('B'), [TSym(EPSILON_CHAR)]),
            Rule(NSym('C'), [TSym('c')])
        ]

        self.assertEqual(build_first_sets(rules),
                         {
                             'A': set(['c']),
                             'B': set([EPSILON_CHAR]),
                             'C': set(['c'])
                         })

        # A -> BC
        # B -> epsilon
        # C -> epsilon
        rules = [
            Rule(NSym('A'), [NSym('B'), NSym('C')]),
            Rule(NSym('B'), [TSym(EPSILON_CHAR)]),
            Rule(NSym('C'), [TSym(EPSILON_CHAR)])
        ]

        self.assertEqual(build_first_sets(rules),
                         {
                             'A': set([EPSILON_CHAR]),
                             'B': set([EPSILON_CHAR]),
                             'C': set([EPSILON_CHAR])
                         })

class TestFollowSets(unittest.TestCase):
    pass
