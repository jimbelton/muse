#!/usr/bin/python

import os
import re

from muse.MuseFile import MuseFile

class AudioFile(MuseFile):
    def __init__(self, filePath, options = {}):
        MuseFile.__init__(self, filePath, options)
        self.audioMd5 = None

    # Override this base method in derived classes. This method includes the entire file in the audioMd5 checksum
    #
    def readFile(self):
        if self.audioMd5:
            return

        self.open()
        self.audioMd5 = md5.new(self.stream.read())
        self.close()

    def compareAudio(self, other):
        self.readFile()
        other.readFile()
        return self.audioMd5.digest() == other.audioMd5.digest()
