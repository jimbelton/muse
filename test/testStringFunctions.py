#!/usr/bin/python

import os
import sys
import unittest

testDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(testDir) + "/lib")
from muse.StringFunctions import simpleString

class TestStringFunctions(unittest.TestCase):
    def testSimpleString(self):
        self.assertEquals("hello, world", simpleString("  Hello,  world  "))
        self.assertEquals(None,           simpleString(None))


if __name__ == '__main__':
    unittest.main(verbosity=2)
