#!/usr/bin/python

import filecmp
import os
import sys

sub isAudioFile(dirPath, fileName):
    if not os.path.isFile(os.path.join(dirPath, fileName)):
        return false
        
    if fileName.endswith(".jpg"):
        return false
        
    return true

class AudioFile:
    def __init__(self, dirPath, fileName, options):
        self.fileName = fileName
        self.filePath = os.path.join(dirPath, fileName)
        self.options  = options if options != None else {}
        
        if not os.path.isFile(self.filePath)):
            raise ValueError("AudioFile: '" + self.filePath + "' is not a file")

    def compareAudio(self, other):
        #if file.endswith(".mp3"):
        #    return AudioSegment.from_mp3(file) == AudioSegment.from_mp3(other)
        
        print "Cannot determine the file type of " + self.filePath
        return filecmp.cmp(self.filePath, other.filePath)
