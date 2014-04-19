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
        self.md5      = md5.new(self.stream.read())
        self.audioMd5 = self.md5
        self.close()

    def compareAudio(self, other):
        self.readFile()
        other.readFile()
        return self.audioMd5.digest() == other.audioMd5.digest()

    def isPreferredTo(self, other, options = None):
        options = options if options else self.options
        
        if self.getSize() == other.getSize():
            if self.compareAudio(other):
                print "Identical audio in files " + self.filePath + " and " + other.filePath
            else:
                print "Same sized files " + self.filePath + " and " + other.filePath
        else:
            print "Same named files " + self.filePath + " and " + other.filePath
