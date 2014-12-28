import os
import sys

from muse.Factory import createAudioFile
from muse.Mp3File import Mp3FileError
from muse.Options import warn

class Library:
    def __init__(self, library, subdir = ".", artistRe = None, albumRe = None, titleRe = None):
        os.chdir(library)
        self.files        = {}
        self.sizes        = {}
        self.artists      = {}
        self.artistMaxLen = len("Artist or Group")
        self.albumMaxLen  = len("Album")
        self.titleMaxLen  = len("Song")

        if subdir[0] != '.':
            subdir = "./" + subdir

        for dirPath, subDirs, files in os.walk(subdir):
            for file in files:
                filePath  = dirPath + "/" + file

                try:
                    audioFile = createAudioFile(filePath)

                    if not audioFile:
                        continue

                    key = file.lower()

                    if key in self.files:
                        warn("Ignoring duplicate file", filePath)
                        continue

                    self.files[key] = audioFile
                    #print filePath

                    artist = audioFile.artist if audioFile.artist else "Unknown"
                    album  = audioFile.album  if audioFile.album  else "Unknown"
                    title  = audioFile.title

                    if artist not in self.artists:
                        self.artists[artist] = {'artist': audioFile.artist, 'albums': {}}
                        self.artistMaxLen    = max(self.artistMaxLen, len(audioFile.artist))

                    if album not in self.artists[artist]['albums']:
                        self.artists[artist]['albums'][album] = {'album': audioFile.album, 'songs': {}}
                        self.albumMaxLen                      = max(self.albumMaxLen, len(audioFile.album))

                    if title not in self.artists[artist]['albums'][album]['songs']:
                        self.artists[artist]['albums'][album]['songs'][title] = audioFile
                        self.titleMaxLen                                      = max(self.titleMaxLen, len(audioFile.title))

                except Mp3FileError as error:
                    warn("Skipping invalid MP3 file (error %s)" % str(error), filePath)
                    continue

#                        otherFile = allFiles[key]
#                        score     = audioFile.isPreferredTo(otherFile)
#
#                        if arguments["--noaction"]:
#                            if score < 0:
#                                print "%s is prefered to %s by %d points" % (file.filePath, otherFile.filePath, -score)
#                            elif score > 0:
#                                print "%s is prefered to %s by %d points" % (otherFile.filePath, file.filePath, -score)
#
#                        elif score < 0:
#                            otherFile.remove()
#                        elif score > 0:
#                            file.remove()
#                        else:
#                            print "Can't choose between %s and %s (try -fn to see what force would do)" % (ile.filePath, otherFile.filePath)
#
#                    else:
#                        allFiles[key] = audioFile
#
#                    if arguments["--metadata"]:
#                        audioFile.reconcile()
#
#                    if backup and not os.path.isfile(backup + relPath + "/" + file):
#                        if not missingRoot:
#                            print backup + relPath + " does not contain file " + file
#
    def getArtists(self):
        return sorted(self.artists.keys())

    def getAlbums(self, artist):
        return sorted(self.artists[artist]['albums'].keys())

    def getSongs(self, artist, album):
        return sorted(self.artists[artist]['albums'][album]['songs'].keys())

    def display(self):
        print "%-*s | %-*s | %-*s" % (self.artistMaxLen, "Artist or Group", self.albumMaxLen, "Album", self.titleMaxLen, "Song")
        print "%s-+-%s-+-%s" % (self.artistMaxLen * "-", self.albumMaxLen * "-", self.titleMaxLen * "-")

        for artist in self.getArtists():
            for album in self.getAlbums(artist):
                for song in self.getSongs(artist, album):
                    print "%-*s | %-*s | %-*s" % (self.artistMaxLen, artist, self.albumMaxLen, album, self.titleMaxLen, song)


