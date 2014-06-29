#!/usr/bin/python

import os
import sys
import unittest

testDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(testDir) + "/lib")
from muse.Factory import createAudioFile
from muse.Options import options

options['warning'] = True

class TestMuse(unittest.TestCase):
    def testAlice(self):
        alice = createAudioFile(testDir + "/data/A/Alice In Chains/Alice in Chains - Them Bones.mp3")
        alice.readFile()
        self.assertEqual(alice.id3v2version, "ID3v2.3.0")
        self.assertTrue(not alice.unsynchronization, "Unsynchronization flag is set")
    
    def testJimmy(self):
        jimmy = createAudioFile(testDir + "/data/J/Jimmy Eat World/Bleed American/Jimmy Eat World - The Middle.mp3")
        jimmy.readFile()
        self.assertEqual(jimmy.id3v2version, "ID3v2.3.0")
        self.assertTrue(not jimmy.unsynchronization, "Unsynchronization flag is set")

if __name__ == '__main__':
    unittest.main(verbosity=2)
