import os
import re
import string
import sys

from muse.MuseFile import MuseFile

class AudioFile(MuseFile):
    dirPattern  = re.compile(r'(?:\./)?(?:([^/])/)?(?:([^/]+)/)?(?:.+/)?([^/]*)?$')
    filePattern = re.compile(r'(?:([^-]+?)\s*-\s+)?(?:([^-]+?)\s*-\s+)?(?:([^-]+?)\s*-\s+)?(?:.*-\s+)?(.+)\..+$')
    
    def __init__(self, filePath, options = {}):
        MuseFile.__init__(self, filePath, options)
        self.md5 = None
        
        # Determine meta-data from file path
        
        (dirName, fileName) = os.path.split(filePath)
        match = AudioFile.dirPattern.match(dirName)
        
        if not match:
            sys.exit("AudioFile: Failed to parse directory name " + dirName)

        self.dirLetter = match.group(1)
        self.dirArtist = match.group(2)
        self.dirAlbum  = match.group(3)
        
        if not match.group(2) and match.group(3):
            self.dirAlbum  = None
            
            if self.dirLetter or len(match.group(3)) > 1:
                self.dirArtist = match.group(3)
            else:
                self.dirLetter = match.group(3)
       
        #print "Directory: Letter %s Artist %s Album %s" % (self.dirLetter, self.dirArtist, self.dirAlbum)
        match = AudioFile.filePattern.match(fileName)
        
        if not match:
            sys.exit("AudioFile: Failed to parse file name " + fileName)
    
        self.fileArtist = match.group(1)
        self.fileAlbum  = match.group(2)
        self.fileTrack  = match.group(3)
        self.fileTitle  = match.group(4)
        
        if not match:
            sys.exit("AudioFile: Failed to parse file name " + dirName)
                
        #print "File name: Letter %s Artist %s Album %s Track %s Song %s" % (self.dirLetter, self.fileArtist, self.fileAlbum, self.fileTrack, self.fileTitle)
        
    # Override this base method in derived classes. This method includes the entire file in the audioMd5 checksum
    #
    def readFile(self):
        if self.md5:
            return

        self.open()
        self.md5      = md5.new(self.stream.read())
        self.audioMd5 = self.md5
        self.close()
        
    def compare(self, other):
        self.readFile()
        other.readFile()
        return self.md5.digest() == other.md5.digest()

    def compareAudio(self, other):
        self.readFile()
        other.readFile()
        return self.audioMd5.digest() == other.audioMd5.digest()

    def isPreferredTo(self, other, options = None):
        options = options if options else self.options
        
        if self.getSize() == other.getSize():
            if self.compareAudio(other):
                if self.compare(other):
                    print "Identical files " + self.filePath + " and " + other.filePath
                else:
                    print "Identical audio in files " + self.filePath + " and " + other.filePath
            else:
                print "Same sized files " + self.filePath + " and " + other.filePath
        else:
            print "Same named files " + self.filePath + " and " + other.filePath
