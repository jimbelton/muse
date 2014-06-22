import md5
import os
import struct
import sys

from muse.AudioFile import AudioFile
from muse.Options   import getOption

def bigEndianInteger(byteString):
    integer = 0
    
    for byte in byteString:
        integer = integer * 8 + byte
    
    return integer

class Mp3FileError(Exception):
    def __init__(self, filePath, offset, message):
        self.filePath = filePath
        self.offset   = offset
        self.message  = message

    def __str__(self):
        return  "%s(%d): %s" % (self.filePath, self.offset, self.message)

class Mp3File(AudioFile):
    def expect(self, description, actual, expected):
        if getOption('--warning') and actual != expected:
            sys.stderr.out("warning: %s(%d): %s was %s but expected %s" 
                           % (self.filePath, self.stream.tell(), description, actual, expected))
        
        return actual
        
    def require(self, description, actual, expected):
        if actual != expected:
            sys.exit("error: %s(%d): %s was %s but required %s" % (self.filePath, self.stream.tell(), description, actual, expected))
        
        return actual
        
    def requireMember(self, description, actual, expectedSet):
        if not actual in expectedSet:
            sys.exit("error: %s(%d): %s was %s but required to be in %s" 
                     % (self.filePath, self.stream.tell(), description, actual, expectedSet))
        
        return actual

    def readFromTag(self, length):
        assert length <= self.tagLength
        self.tagLength -= length
        return self.read(length)

    def readID3v2Tag(self, header):
        header += self.read(6, "ID3v2 header", {})
        self.md5.update(header)
        self.id3v2version = self.expect("version", "ID3v2.%d.%d" % (ord(header[3]), ord(header[4])), "ID3v2.3.0")
        tagFlags = ord(header[5])
        self.unsynchronization = tagFlags & 0x80
        self.expect("experimental flag", tagFlags & 0x20, 0)
        self.require("undefined tag flags", tagFlags & 0x1F, 0)
        self.tagLength = 0
        
        for char in header[6:]:
            self.tagLength <<= 7
            self.tagLength +=  ord(char)
            
        # If the extended header flag is set
        if tagFlags & 0x40:
            extendedHeader       = readFromTag(10)
            extendedHeaderLength = this.expectedSet("extended head length", bigEndianInteger(extendedHeader[:4]), {6, 10})
            
        body = self.read(self.tagLength, "ID3v2 tag body", {})
        self.md5.update(body)
        
    def readFile(self):
        if self.md5:
            return

        self.open()
        self.md5 = md5.new()
        
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
                
            self.md5.update(header)
            self.audioMd5 = md5.new(header)
            remainder     = self.stream.read()
            self.md5.update(remainder)
            self.audioMd5.update(remainder)
            break
            
        self.close()
