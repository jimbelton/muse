#!/usr/bin/python

import os
import re

from muse.MuseFile import MuseFile

class AudioFile(MuseFile):
    def __init__(self, filePath, options = {}):
        MuseFile.__init__(self, filePath, options)
        self.audioMd5 = None

    def compareAudio(self, other):
        self.readFile()
        other.readFile()
        return self.audioMd5.digest() == other.audioMd5.digest()
