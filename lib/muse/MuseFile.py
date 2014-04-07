#!/usr/bin/python

import filecmp
import os
import re

class MuseFileError(Exception):
    def __init__(self, filePath, offset, message):
        self.filePath = filePath
        self.offset   = offset
        self.message  = message
         
    def __str__(self):
        return  "%s(%d): %s" % (self.filePath, self.offset, self.message)

class MuseFile:
    def __init__(self, filePath, options):
        self.filePath = filePath
        self.fileName = os.path.basename(filePath)
        self.options  = options if options != None else {}
        self.stream   = None
        
        if not os.path.isfile(filePath):
            raise ValueError("MuseFile: '" + filePath + "' is not a file")
            
    def open(self):
        if self.stream != None:
            raise MuseFileError(self.filePath, 0, "Attempt to open file when it's already open")
            
        self.stream = open(self.filePath, "rb")
            
    def read(self, length, message, options = {}):
        if (self.stream == None):
            raise MuseFileError(self.filePath, 0, "Attempt to read file when it's not open")

        content = self.stream.read(length)
        actual  = len(content)
        
        if actual == length or 'trunc' in options:
            return content

        if actual > 0:
            raise MuseFileError(self.filePath, self.stream.tell(), "Partial value at EOF: " + message)

        if 'eof' in options:
            return ""

        raise MuseFileError(self.filePath, self.stream.tell(), "EOF: " + message)

    def close(self):
        self.stream.close()
        self.stream = None
