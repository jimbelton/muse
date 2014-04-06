#!/usr/bin/python

import filecmp
import os
import struct
import sys
from muse.AudioFile import AudioFile

class Mp3FileError(Exception):
    def __init__(self, filePath, offset, message):
        self.filePath = filePath
        self.offset   = offset
        self.message  = message
         
    def __str__(self):
        return  "%s(%d): %s" % (self.filePath, self.offset, self.message)

class Mp3File(AudioFile):
    def readID3v2Tag(self, header):
        header += self.input.read(6)
        
        if len(header) < 10:
            raise Mp3FileError(self.filePath, offset, "%d byte truncated ID3v2 header at end of file" % (len(header)))
            
        self.offset += 6;
        length       = 0
        
        for char in header[6:]:
            length <<= 7
            length +=  ord(char)
            
        print "Length from ID3v2Tag: %d" % (length)
        body = self.input.read(length)
        self.offset += length;
        
    def read(self):
        if self.audioMd5:
            return

        print "About to read " + self.filePath
        self.input  = open(self.filePath, "rb")
        self.offset = 0
        
        while True:
            header = self.input.read(4)
            
            if len(header) == 0:
                break
                
            if len(header) < 4:
                raise Mp3FileError(self.filePath, offset, "%d extra bytes at end of file" % (len(header)))
                
            self.offset += 4
            
            if (header[:3] == "ID3"):
                self.readID3v2Tag(header)
                continue
                
            words = struct.unpack(">l", header)
            
            if (words[0] & 0xFFFF0000) == 0xFFFB0000:
                print "Found an mp3 header at offset %d" % (self.offset)
                sys.exit(0)
                
            print header[0:2]
            print "Unknown tag at offset %d: '%08x'" % (self.offset, words[0])
            sys.exit(0)
