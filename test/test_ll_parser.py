import unittest
from pycc.ll_parser import *
from pycc.grammar import *
from pycc.constants import *
from test.test_helpers import *

class TestIntegration(unittest.TestCase):
    def test_parse(self):
        parser = LLParser(integration_test_grammar)

        self.assertTrue(parser.parse('0'))
        self.assertTrue(parser.parse('0+0*0'))
        self.assertTrue(parser.parse('(0+0)*(0+0)'))

        self.assertFalse(parser.parse('0+'))
        self.assertFalse(parser.parse('(0+0'))
        self.assertFalse(parser.parse('(0+0)*0)'))
