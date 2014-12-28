import md5
import os
import struct
import sys

from muse.AudioFile import AudioFile
from muse.Options   import getOption, warn

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
            if self.expect("padding byte", ord(paddingChar), 0) != 0:
                if padding.find("\xFF\xFF\xFF") >= 0:
                    raise Mp3FileError(self.filePath, self.stream.tell() - len(padding) + padding.find("\xFF\xFF\xFF"),
                                       "Found an MP3 sync tag in ID3 tag padding")

                break

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
        if length > self.tagLeft:
            raise Mp3FileError(self.filePath, self.stream.tell(),
                               "%s: length to read %d exceeds remaining tag length %d" % (message, length, self.tagLeft))

        self.tagLeft -= length
        data = self.read(length, message)
        self.md5.update(data)
        return data

    # Return: true if read successfully, false if not
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

        try:
            frameBody = self.readFromTag(frameBodyLength, "ID3v2 '%s' frame body" % (frameId))

        except Mp3FileError as error:
            if getOption('warning'):
                sys.stderr.write("warning: " + str(error) + ": skipping remainder of ID3v2 tag\n")

            return False

        if (self.expect("ignoring '%s' frame: compression flag" % (frameId), frameFlags & 0x80, 0) or
            self.expect("ignoring '%s' frame: encryption flag"  % (frameId), frameFlags & 0x40, 0)):
            return True

        if frameId[0] == "T" or frameId == "IPLS":
            encoding = ord(frameBody[0])
            self.requireMember("encoding descriptor for %s frame" % (frameId), encoding, {0, 1, 2, 3})
            value = frameBody[1:].decode(id3v2EncodingToPythonEncoding[encoding], errors="strict")

            if frameId == "TRCK":
                if value == "":
                    warn("TRCK tag is present but empty (ignoring it)", self.filePath, self.stream.tell())
                    return False

                self.track = int(value.split("/")[0])

        else:
            value = frameBody

        self.frames[frameId] = value
        return True

    def readID3v2Tag(self, header):
        header += self.read(7, "ID3v2 header")
        self.md5.update(header)
        self.id3v2version = self.expectMember("version", "ID3v2.%d.%d" % (ord(header[3]), ord(header[4])),
                                              {"ID3v2.3.0", "ID3v2.4.0"})
        tagFlags = ord(header[5])
        self.unsynchronization = tagFlags & 0x80
        self.require("unsynchronization is not yet supported", self.unsynchronization, 0)
        self.expect("experimental flag", tagFlags & 0x20, 0)
        self.require("undefined tag flags", tagFlags & 0x1F, 0)
        self.id3Length = 0

        for char in header[6:]:
            self.id3Length <<= 7
            self.id3Length +=  ord(char)

        self.tagLeft    = self.id3Length
        self.id3Length += 10

        # If the extended header flag is set
        if tagFlags & 0x40:
            extendedHeader       = self.readFromTag(10, "ID3v2 tag extended header")
            extendedHeaderLength = self.expectMember("extended head length", bigEndianInteger(extendedHeader[:4]), {6, 10})

            if extendedHeaderLength == 10:
                crc = self.readFromTag(4, "ID3v2 tag CRC")

        while self.tagLeft >= 10 and self.readID3v2Frame():
            pass

        padding = self.readFromTag(self.tagLeft, "ID3v2 padding")
        self.expectPadding(padding)

    def readFile(self):
        if self.md5:
            return

        self.open()
        self.md5    = md5.new()

        while True:
            header = self.read(3, "header tag", {'eof'})

            if len(header) == 0:    # EOF
                raise Mp3FileError(self.filePath, self.stream.tell(), "EOF without any MP3 content")

            if (header == "ID3"):
                self.readID3v2Tag(header)
                continue

            # Check for sync bytes
            #
            if header[:2] != "\xFF\xFB":
                discarded = 1
                header = header[1:]

                while header != "\xFF\xFB":
                    discarded += 1
                    header = header[1] + self.read(1, "sync byte", {'eof'})

                    if len(header) < 2:
                        raise Mp3FileError(self.filePath, self.stream.tell(), "EOF searching for MP3 sync bytes")

                warn("Found sync bytes after skipping %d bytes\n" % (discarded), self.filePath, self.stream.tell())

            self.md5.update(header)
            self.audioMd5 = md5.new(header)
            remainder     = self.stream.read()
            self.md5.update(remainder)
            self.audioMd5.update(remainder)
            break

        #print "'" + self.frames['TPE1'] + "' == '" + (self.dirArtist if self.dirArtist else "") + "'"
        #self.score += 1 if self.frames.get('TPE1') == self.dirArtist  else 0
        #self.score += 1 if self.frames.get('TPE1') == self.fileArtist else 0
        #self.score += 1 if self.frames.get('TALB') == self.dirAlbum   else 0
        #self.score += 1 if self.frames.get('TALB') == self.fileAlbum  else 0
        #self.score += 1 if self.frames.get('TRCK') == self.fileTrack  else 0
        #self.score += 1 if self.frames.get('TIT2') == self.fileTitle  else 0
        self.close()

    def reconcile(self):
        self.readFile()
        super(Mp3File, self).reconcile()
