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
    def __init__(self, filePath):
        self.filePath = filePath
        self.stream   = None
        self.stat     = None
        
        if not os.path.isfile(filePath):
            raise ValueError("MuseFile: '" + filePath + "' is not a file")
    
    def getStat(self):
        if not self.stat:
            self.stat = os.stat(self.filePath)

        return self.stat
        
    def getCreationTime(self):
        return self.getStat().st_ctime
        
    def getModificationTime(self):
        return self.getStat().st_mtime
        
    def getSize(self):
        return self.getStat().st_size
        
    def open(self):
        if self.stream != None:
            raise MuseFileError(self.filePath, 0, "Attempt to open file when it's already open")
            
        self.stream = open(self.filePath, "rb")
            
    def read(self, length, message, options = set()):
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
        if self.stream:
            self.stream.close()
            
        self.stream = None

    def remove(self):
        self.close()
        os.remove(self.filePath)
