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
        
        if not os.path.isfile(filePath):
            raise ValueError("AudioFile: '" + filePath + "' is not a file")

    #def compareAudio(self, other):
    #    print "Cannot determine the file type of " + self.filePath
    #    return filecmp.cmp(self.filePath, other.filePath)
