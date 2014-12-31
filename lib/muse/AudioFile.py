import md5
import os
import re
import string
import sys

from muse.MuseFile        import MuseFile
from muse.StringFunctions import reconcileStrings, safeAppend, simpleString
from muse.Options         import error, getOption, takeAction, warn

class AudioFileError(Exception):
    def __init__(self, filePath, message):
        self.filePath = filePath
        self.message  = message

    def __str__(self):
        return  "%s: %s" % (self.filePath, self.message)

class AudioFile(MuseFile):
    splitPattern       = re.compile(r'(.*)/([^/]+?)(?:\.([^\./]+))?$')
    dirPattern         = re.compile(r'(?:\./)?(?:([^/])/)?(?:([^/]+)/)?(?:.+/)?([^/]*)?$')
    filePattern        = re.compile(r'(?:([^-]+?)\s*-\s+)?(?:([^-]+?)\s*-\s+)?(?:([^-]+?)\s*-\s+)?(?:.*-\s+)?(.+)$')
    numericPattern     = re.compile(r'(\d+)(?:\.)?\s*(.*)$')
    artistAlbumPattern = re.compile(r'(\S.*\S)\s+\[(.+)\]$')
    withArtistPattern  = re.compile(r'(\S.*\S)\s*&\s*(\S.*\S)$')

    def __init__(self, filePath, rootPath=None):
        MuseFile.__init__(self, filePath, rootPath)
        self.artist = None
        self.album  = None
        self.md5    = None
        self.frames = {}

        # Determine meta-data from file path

        match = AudioFile.splitPattern.match(filePath)

        if not match:
            raise AudioFileError(filePath, "Failed to parse file path")

        (dirName, fileName, fileExt) = match.group(1, 2, 3)
        match = AudioFile.dirPattern.match(dirName)

        if not match:
           raise AudioFileError(filePath, "Failed to parse directory name " + dirName)

        (dirLetter, dirArtist, dirAlbum) = match.group(1, 2, 3)

        if not match.group(2) and match.group(3):
            dirAlbum  = None

            if dirLetter or len(match.group(3)) > 1:
                dirArtist = match.group(3)
            else:
                dirLetter = match.group(3)

        #print "Directory: Letter %s Artist %s Album %s" % (dirLetter, dirArtist, dirAlbum)
        match = AudioFile.filePattern.match(fileName)

        if not match:
            raise AudioFileError(filePath, "Failed to parse file name " + fileName)

        (fileArtist, fileAlbum, self.track, self.title) = match.group(1, 2, 3, 4)
        #print ("File name: Letter %s Artist %s Album %s Track %s Song %s Ext %s" %
        #       (dirLetter, fileArtist, fileAlbum, self.track, self.title, fileExt))

        self.artist = reconcileStrings(dirArtist, fileArtist, default="Unknown")

        if self.artist == "Unknown":
            warn("Failed to determine an artist from the filepath", filePath)

        elif self.artist == None:
            self.artist = dirArtist
            match       = AudioFile.numericPattern.match(fileArtist)

            if match and self.track == None:
                self.track  = match.group(1)
                fileArtist  = match.group(2)

            if fileArtist:
                match = AudioFile.artistAlbumPattern.match(fileArtist)

                if match and reconcileStrings(dirArtist, match.group(1)) and reconcileStrings(dirAlbum, match.group(2)):
                    fileAlbum = match.group(2)
                else:
                    match = AudioFile.withArtistPattern.match(fileArtist)

                    if (not (match and (reconcileStrings(match.group(1), dirArtist) or reconcileStrings(match.group(2), dirArtist)))
                        and not simpleString(dirArtist) == simpleString(fileArtist).replace("_", " ")):
                        error("Directory artist '%s' differs from file name artist '%s'" % (dirArtist, fileArtist), filePath)

        self.album = reconcileStrings(dirAlbum, fileAlbum, default="Unknown")

        if self.album == "Unknown":
            warn("Failed to determine an album from the filepath", filePath)

        elif self.album == None:
            self.album = dirAlbum

            if fileArtist.isdigit() and reconcileStrings(fileAlbum, dirArtist):
                self.track = fileArtist

            elif not reconcileStrings(fileAlbum, dirArtist):
                error("Directory album '%s' differs from file name album '%s'" % (dirAlbum, fileAlbum), filePath)

        newPath = ("%s/%s%s%s%s.%s"
                   % (dirName, safeAppend(self.artist, " - ", suppress="Unknown"), safeAppend(self.album, " - ", suppress="Unknown"),
                      safeAppend(self.track, " - "), self.title, fileExt))

        if getOption("fix", default=False) and newPath != filePath and takeAction("rename %s to %s" % (filePath, newPath)):
            os.rename(filePath, newPath)
            os.utime(newPath, None)

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

    def isPreferredTo(self, other):
        #print "%s %s %s %s %s" % (self.dirLetter, self.dirArtist, self.dirAlbum, self.fileArtist, self.fileTitle)

        if self.getSize() == other.getSize():
            if self.compareAudio(other):
                if self.compare(other):
                    print "Identical files " + self.getPath() + " and " + other.filePath
                else:
                    print "Identical audio in files " + self.getPath() + " and " + other.filePath

            else:
                print "Same sized files " + self.getPath() + " and " + other.filePath

            return other.score - self.score

        else:
            print "Same named files " + self.getPath() + " and " + other.filePath
            return other.score - self.score if getOption('forced', default = False) else 0

    trackNumberPattern = re.compile(r'(\d+)$')

    def reconcile(self):
        self.readFile()
        simpleArtist = reconcileStrings(self.dirArtist, self.fileArtist, self.frames.get('TPE1'))
        simpleAlbum  = reconcileStrings(self.dirAlbum,  self.fileAlbum,  self.frames.get('TALB'))
        simpleTitle  = reconcileStrings(                self.fileTitle,  self.frames.get('TIT2'))

        if (simpleArtist == None):
            if (self.dirArtist, self.fileArtist, self.frames.get('TPE1')) == (None, None, None):
                warn("Can't identify an artist", self.getPath())
            else:
                warn("Conflicting artists (tag %s)" % (self.frames.get('TPE1')), self.getPath())

            return

        if (simpleAlbum == None):
            if (self.dirAlbum, self.fileAlbum, self.frames.get('TALB')) == (None, None, None):
                warn("Can't identify an album", self.getPath())
            else:
                warn("Conflicting albums (tag %s)" % (self.frames.get('TALB')), self.getPath())

            return

        if (simpleTitle == None):
            if (self.fileTitle, self.frames.get('TIT2')) == (None, None, None):
                warn("Can't identify a title", self.getPath())
            else:
                warn("Conflicting titles (tag %s)" % (self.frames.get('TIT2')), self.getPath())

            return

        if self.dirArtist:
            if self.dirArtist == self.fileArtist:
                if self.frames.get('TPE1') != self.fileArtist:
                    print "%s: artist tag %s differs from directory/file artist %s" % (self.getPath(), self.frames.get('TPE1'),
                                                                                       self.fileArtist)
            elif self.dirArtist == self.frames.get('TPE1'):
                if simpleString(self.dirArtist) == simpleString(self.fileArtist):
                    if takeAction("rename file %s to %s to match directory/tagged artist %s"
                                  % (self.getPath(), self.getPath().replace(self.fileArtist, self.dirArtist), self.dirArtist)):
                        os.rename(self.getPath(), self.getPath().replace(self.fileArtist, self.dirArtist))
                elif self.fileArtist == None:
                    if self.fileName.endswith(self.frames.get('TIT2')):
                        head  = self.fileName[:-len(self.frames.get('TIT2'))].strip()
                        match = self.trackNumberPattern.match(head)

                        if match:
                            if int(match.group(1)) == self.track:
                                toPath = "%s/%s - %d - %s.self.dirName"
                                if takeAction("rename file %s to %s to match directory/tagged artist %s"
                                              % (self.getPath(), self.getPath().replace(self.fileArtist, self.dirArtist), self.dirArtist)):
                                    os.rename(self.getPath(), self.getPath().replace(self.fileArtist, self.dirArtist))


                        print "'" + head + "'"
                        print ("%s: filename ends with title %s (no file artist; directory/tagged artist %s)"
                               % (self.getPath(), self.frames.get('TIT2'), self.dirArtist))
                    else:
                        print "%s: no file artist parsed (directory/tagged artist %s)" % (self.getPath(), self.dirArtist)
                else:
                    print "%s: file artist %s differs from directory/tagged artist %s" % (self.getPath(), self.fileArtist,
                                                                                          self.dirArtist)
