#!/usr/bin/python

import os
import sys
import unittest

testDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(testDir) + "/lib")
from muse.StringFunctions import simpleString, reconcileStrings, safeAppend

class TestStringFunctions(unittest.TestCase):
    def testSimpleString(self):
        self.assertEquals("hello, world", simpleString("  Hello,  world  "))
        self.assertEquals(None,           simpleString(None))

    def testReconcileStrings(self):
        self.assertEquals("Beatles", reconcileStrings("Beatles", "The Beatles",   None))
        self.assertEquals(None,      reconcileStrings("The Who", "The Guess Who", None))
        self.assertEquals("Unknown", reconcileStrings(None,      None,            default = "Unknown"))

    def testSafeAppend(self):
        self.assertEquals("A - ", safeAppend("A",  " - "))
        self.assertEquals("",     safeAppend(None, " - "))
        self.assertEquals("",     safeAppend("Unknown", " - ", suppress="Unknown"))

if __name__ == '__main__':
    unittest.main(verbosity=2)
