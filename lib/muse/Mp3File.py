import md5
import os
import struct
import sys

from muse.AudioFile import AudioFile
from muse.Options   import getOption

def bigEndianInteger(byteString):
    integer = 0
    
    for byte in byteString:
        integer = integer * 8 + ord(byte)
    
    return integer

class Mp3FileError(Exception):
    def __init__(self, filePath, offset, message):
        self.filePath = filePath
        self.offset   = offset
        self.message  = message

    def __str__(self):
        return  "%s(%d): %s" % (self.filePath, self.offset, self.message)

# ID3v2 string encoding types are the byte values 0 ... 3
# 
id3v2EncodingToPythonEncoding = ("iso-8859-1", "utf_16", "utf_16_be", "utf_8")

class Mp3File(AudioFile):
    
    def expect(self, description, actual, expected):
        if getOption('warning') and actual != expected:
            sys.stderr.write("warning: %s(%d): %s was %s but expected %s\n" 
                             % (self.filePath, self.stream.tell(), description, actual, expected))
        
        return actual
    
    def expectMember(self, description, actual, expectedSet):
        if getOption('warning') and not actual in expectedSet:
            sys.stderr.write("warning: %s(%d): %s was %s but required to be in %s\n"
                             % (self.filePath, self.stream.tell(), description, actual, expectedSet))
                               
        return actual                      

    def expectPadding(self, padding):
        for paddingChar in padding:
            self.expect("padding byte", ord(paddingChar), 0)
            
        return padding
        
    def require(self, description, actual, expected):
        if actual != expected:
            raise Mp3FileError(self.filePath, self.stream.tell(), "%s was %s but required %s" % (description, actual, expected))
        
        return actual
        
    def requireMember(self, description, actual, expectedSet):
        if not actual in expectedSet:
            raise Mp3FileError(self.filePath, self.stream.tell(), 
                               "%s was %s but required to be in %s"  % (description, actual, expectedSet))
        
        return actual

    def readFromTag(self, length, message):
        if length > self.tagLength:
            raise Mp3FileError(self.filePath, self.stream.tell(), 
                               "%s: length to read %d exceeds remaining tag length %d" % (message, length, self.tagLength))
                               
        self.tagLength -= length
        data = self.read(length, message)
        self.md5.update(data)
        return data
        
    def readID3v2Frame(self):
        frameHeader = self.readFromTag(10, "ID3v2 frame header")
        
        if ord(frameHeader[:1]) == 0:
            self.expectPadding(frameHeader[1:])
            return
            
        frameId         = frameHeader[:4]
        frameBodyLength = bigEndianInteger(frameHeader[4:8])
        frameFlags      = bigEndianInteger(frameHeader[9:10])
        
        if frameFlags & 0x20:
            self.readFromTag(1, "ID3v2 frame group identifier byte")
            
        frameBody = self.readFromTag(frameBodyLength, "ID3v2 %s frame body" % (frameId))
        
        if (self.expect("ignoring %s frame with compression flag" % (frameId), frameFlags & 0x80, 0) or 
            self.expect("ignoring %s frame encryption flag"  % (frameId), frameFlags & 0x40, 0)):
            return
            
        if frameId[0] == "T" or frameId == "IPLS":
            encoding = ord(frameBody[0])
            self.requireMember("encoding descriptor for %s frame" % (frameId), encoding, {0, 1, 2, 3})
            value = frameBody[1:].decode(id3v2EncodingToPythonEncoding[encoding], errors="strict")
                
        else:
            value = frameBody
            
        self.frames[frameId] = value

    def readID3v2Tag(self, header):
        header += self.read(6, "ID3v2 header")
        self.md5.update(header)
        self.id3v2version = self.expectMember("version", "ID3v2.%d.%d" % (ord(header[3]), ord(header[4])), {"ID3v2.3.0", "ID3v2.4.0"})
        tagFlags = ord(header[5])
        self.unsynchronization = tagFlags & 0x80
        self.require("unsynchronization is not yet supported", self.unsynchronization, 0)
        self.expect("experimental flag", tagFlags & 0x20, 0)
        self.require("undefined tag flags", tagFlags & 0x1F, 0)
        self.tagLength = 0
        
        for char in header[6:]:
            self.tagLength <<= 7
            self.tagLength +=  ord(char)
            
        # If the extended header flag is set
        if tagFlags & 0x40:
            extendedHeader       = self.readFromTag(10, "ID3v2 tag extended header")
            extendedHeaderLength = self.expectedSet("extended head length", bigEndianInteger(extendedHeader[:4]), {6, 10})
            
            if extendedHeaderLength == 10:
                crc = self.readFromTag(4, "ID3v2 tag CRC")
                
        self.frames = {}

        while self.tagLength >= 10:
            self.readID3v2Frame()

        body = self.readFromTag(self.tagLength, "ID3v2 padding")
        self.md5.update(body)
        
    def readFile(self):
        if self.md5:
            return

        self.open()
        self.md5 = md5.new()
        
        while True:
            header = self.read(4, "header tag", {'eof'})
            
            if len(header) == 0:    # EOF
                raise Mp3FileError(self.filePath, self.stream.tell(), "EOF without any mp3 content")
            
            if (header[:3] == "ID3"):
                self.readID3v2Tag(header)
                continue
                
            words = struct.unpack(">l", header)
            
            if (words[0] & 0xFFFF0000) != 0xFFFB0000:
                raise Mp3FileError(self.filePath, self.stream.tell(),
                                   "Unknown tag '%04x%04x'" % ((words[0] >> 4) & 0xFFFF, words[0] & 0xFFFF))
            self.md5.update(header)
                
            self.audioMd5 = md5.new(header)
            remainder     = self.stream.read()
            self.md5.update(remainder)
            self.audioMd5.update(remainder)
            break
    
        #print "'" + self.frames['TPE1'] + "' == '" + (self.dirArtist if self.dirArtist else "") + "'" 
        self.score += 1 if self.frames.get('TPE1') == self.dirArtist  else 0
        self.score += 1 if self.frames.get('TPE1') == self.fileArtist else 0        
        self.score += 1 if self.frames.get('TALB') == self.dirAlbum   else 0
        self.score += 1 if self.frames.get('TALB') == self.fileAlbum  else 0
        self.score += 1 if self.frames.get('TRCK') == self.fileTrack  else 0
        self.score += 1 if self.frames.get('TIT2') == self.fileTitle  else 0
        self.close()

    def reconcile(self):
        self.readFile()
        
        if self.dirArtist == self.fileArtist:
            if self.frames['TPE1'] != self.fileArtist:
                print "%s: artist tag %s differs from directory artist %s" % (self.filePath, self.frames['TPE1'], self.fileArtist)
                    
