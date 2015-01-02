import filecmp
import os
import time
import re

class MuseFileError(Exception):
    def __init__(self, filePath, offset, message):
        self.filePath = filePath
        self.offset   = offset
        self.message  = message

    def __str__(self):
        return  "%s(%d): %s" % (self.filePath, self.offset, self.message)

class MuseFile(object):
    def __init__(self, filePath, rootPath=None):
        self.filePath = filePath
        self.rootPath = rootPath
        self.stream   = None
        self.stat     = None

        if not os.path.isfile(self.getPath()):
            raise ValueError("MuseFile: '%s' is not a file" % self.getPath())

    def getPath(self, filePath=None):
        filePath = filePath if filePath else self.filePath

        if filePath[0] == '/' or not self.rootPath:
            return filePath

        return "%s/%s" % (self.rootPath, filePath)

    def getStat(self):
        if not self.stat:
            self.stat = os.stat(self.getPath())

        return self.stat

    def getCreationTime(self):
        return self.getStat().st_ctime

    def getModificationTime(self):
        return self.getStat().st_mtime

    def getSize(self):
        return self.getStat().st_size

    def open(self):
        if self.stream != None:
            raise MuseFileError(self.getPath(), 0, "Attempt to open file when it's already open")

        self.stream = open(self.getPath(), "rb")

    def read(self, length, message, options = set()):
        if (self.stream == None):
            raise MuseFileError(self.getPath(), 0, "Attempt to read file when it's not open")

        content = self.stream.read(length)
        actual  = len(content)

        if actual == length or 'trunc' in options:
            return content

        if actual > 0:
            raise MuseFileError(self.getPath(), self.stream.tell(), "Partial value at EOF: " + message)

        if 'eof' in options:
            return ""

        raise MuseFileError(self.getPath(), self.stream.tell(), "EOF: " + message)

    def close(self):
        if self.stream:
            self.stream.close()

        self.stream = None

    def move(self, filePath):
        toPath = self.getPath(filePath)
        toDir  = os.path.dirname(toPath)
        print toDir

        if not os.path.exists(toDir):
            os.makedirs(toDir)

        os.rename(self.getPath(), self.getPath(filePath))

    def remove(self):
        self.close()
        os.remove(self.getPath())

    def syncModTime(self, other):
        print self.getPath() + ":" + time.ctime(self.getModificationTime()) + ":" + time.ctime(other.getModificationTime())
        os.utime(self.getPath(), (other.getModificationTime(), other.getModificationTime()))
