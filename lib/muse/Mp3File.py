#!/usr/bin/python

import filecmp
import os
import sys
from muse.AudioFile import AudioFile

class Mp3File(AudioFile):
    def compareAudio(self, other):
        #if file.endswith(".mp3"):
        #    return AudioSegment.from_mp3(file) == AudioSegment.from_mp3(other)
        
        print "Cannot determine the file type of " + self.filePath
        return filecmp.cmp(self.filePath, other.filePath)
