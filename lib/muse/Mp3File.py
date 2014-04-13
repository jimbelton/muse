#!/usr/bin/python

import md5
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
        header += self.read(6, "ID3v2 header", {})
        length  = 0
        
        for char in header[6:]:
            length <<= 7
            length +=  ord(char)
            
        body = self.read(length, "ID3v2 tag body", {})
        
    def readFile(self):
        if self.audioMd5:
            return

        self.open()
        
        while True:
            header = self.read(4, "header tag", {'eof': 'true'})
            
            if len(header) == 0:    # EOF
                raise MuseFileError(self.filePath, self.stream.tell(), "EOF without any mp3 content")
            
            if (header[:3] == "ID3"):
                self.readID3v2Tag(header)
                continue
                
            words = struct.unpack(">l", header)
            
            if (words[0] & 0xFFFF0000) != 0xFFFB0000:
                raise MuseFileError(self.filePath, self.stream.tell(), "Unknown tag '%08x'" % (words[0]))
                
            self.audioMd5 = md5.new(header)
            remainder = self.stream.read()
            self.audioMd5.update(remainder)
            break
            
        self.close()
