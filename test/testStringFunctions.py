#!/usr/bin/python

import os
import sys
import unittest

testDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(testDir) + "/lib")
from muse.StringFunctions import simpleString, reconcileStrings, safeAppend

class TestStringFunctions(unittest.TestCase):
    def testSimpleString(self):
        self.assertEquals("hello, world",     simpleString("  Hello,  world  "))
        self.assertEquals(None,               simpleString(None))
        self.assertEquals("blue oyster cult", simpleString(u"Blue \xD6yster Cult".encode('utf8')))
        self.assertEquals("sonny and cher",   simpleString("Sonny & Cher"))
        self.assertEquals("c, s, n and y",    simpleString("C, S, N, & Y"))

    def testReconcileStrings(self):
        self.assertEquals("Beatles",    reconcileStrings("Beatles",    "The Beatles",     None))
        self.assertEquals(None,         reconcileStrings("The Who",    "The Guess Who",   None))
        self.assertEquals("Unknown",    reconcileStrings(None,         None,              default = "Unknown"))
        self.assertEquals("Black Keys", reconcileStrings("Black Keys", "Black Keys, The", None))

    def testSafeAppend(self):
        self.assertEquals("A - ", safeAppend("A",  " - "))
        self.assertEquals("",     safeAppend(None, " - "))
        self.assertEquals("",     safeAppend("Unknown", " - ", suppress="Unknown"))

if __name__ == '__main__':
    unittest.main(verbosity=2)
