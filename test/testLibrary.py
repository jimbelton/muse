#!/usr/bin/python

import os
import sys
import unittest

testDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(testDir) + "/lib")
from muse.Library import Library

class TestLibrary(unittest.TestCase):
    def testLibrary(self):
        self.library = Library(testDir + "/data")

    def testPartialLibrary(self):
        self.library = Library(testDir + "/data", "A")

if __name__ == '__main__':
    unittest.main(verbosity=2)
