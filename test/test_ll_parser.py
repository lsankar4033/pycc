import unittest
from pycc.ll_parser import *
from pycc.grammar import *
from pycc.constants import *
from test.test_helpers import *

class TestIntegration(unittest.TestCase):
    def test_parse_add_mult(self):
        parser = LLParser(integration_test_grammar)

        self.assertTrue(parser.parse('0'))
        self.assertTrue(parser.parse('0+0*0'))
        self.assertTrue(parser.parse('(0+0)*(0+0)'))

        self.assertFalse(parser.parse('0+'))
        self.assertFalse(parser.parse('(0+0'))
        self.assertFalse(parser.parse('(0+0)*0)'))

    # TODO Test a simple regex grammar
    # Right now, regex_grammar in test_helpers isn't LL(1)...
    def test_parse_regex(self):
        pass


    # TODO - test parse with grammar requiring normalization
