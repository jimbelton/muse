#!/usr/bin/python

import filecmp
import os
import re
#import sys

class AudioFile:
    def __init__(self, filePath, options):
        self.filePath = filePath
        self.fileName = os.path.basename(filePath)
        self.options  = options if options != None else {}
        self.audioMd5 = None
        
        if not os.path.isfile(filePath):
            raise ValueError("AudioFile: '" + filePath + "' is not a file")

    def compareAudio(self, other):
        self.read()
        other.read()
        return self.audioMd5 == other.audioMd5
