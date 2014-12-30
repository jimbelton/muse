import os
import sys

from muse.Factory import createAudioFile
from muse.Mp3File import Mp3FileError
from muse.Options import warn

class Library:
    def __init__(self, library, subdir = ".", artistRe = None, albumRe = None, titleRe = None):
        self.files        = {}
        self.sizes        = {}
        self.artists      = {}
        self.artistMaxLen = len("Artist or Group")
        self.albumMaxLen  = len("Album")
        self.titleMaxLen  = len("Song")

        if subdir[0] != '.':
            subdir = "./" + subdir

        library = os.path.abspath(library)    # Pass this single reference to all strings to conserve memory
        curDir  = os.getcwd()
        os.chdir(library)                     # Keep paths short

        for dirPath, subDirs, dirFiles in os.walk(subdir):
            for file in dirFiles:
                filePath  = dirPath + "/" + file

                try:
                    audioFile = createAudioFile(filePath, rootPath=library)

                    if not audioFile:
                        continue

                    key = file.lower()

                    if key in self.files:
                        warn("Ignoring duplicate file", filePath)
                        continue

                    audioFile.key   = key
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

        os.chdir(curDir)    # Restore the path for the caller

    def getArtists(self):
        return sorted(self.artists.keys())

    def getAlbums(self, artist):
        return sorted(self.artists[artist]['albums'].keys())

    def getTitles(self, artist, album):
        return sorted(self.artists[artist]['albums'][album]['songs'].keys())

    def findSong(self, song):
        if song.key in self.files:
            other = self.files[song.key]

            if song.compare(other):
                print "File %s has the same audio content as %s" % (song.getPath(), other.getPath())
                return other

            else:
                warn("File %s has the same name as %s but is different" % (song.getPath(), other.getPath()))

            return None

    def findSongsInBackup(self, backup, artist, album):
        for song in self.artists[artist]['albums'][album]['songs']:
            backSong = backup.findSong(self.artists[artist]['albums'][album]['songs'][song])

            #if backSong:


    def diff(self, backup, command='compare'):
        libArtists = self.getArtists()
        bakArtists = backup.getArtists()

        while len(libArtists) > 0 or len(bakArtists) > 0:
            if len(bakArtists) == 0 or libArtists[-1] > bakArtists[-1]:
                artist = libArtists.pop()
                print "Library artist " + artist + " not found in backup"

                for album in self.getAlbums(artist):
                    self.findSongsInBackup(backup, artist, album)

                continue

            if len(libArtists) == 0 or bakArtists[-1] > libArtists[-1]:
                artist = bakArtists.pop()
                print "Backup artist " + artist + " not found in library"
                continue

            libArtists.pop()
            bakArtists.pop()

    def display(self):
        print "%-*s | %-*s | %-*s" % (self.artistMaxLen, "Artist or Group", self.albumMaxLen, "Album", self.titleMaxLen, "Title")
        print "%s-+-%s-+-%s" % (self.artistMaxLen * "-", self.albumMaxLen * "-", self.titleMaxLen * "-")

        for artist in self.getArtists():
            for album in self.getAlbums(artist):
                for title in self.getTitles(artist, album):
                    print "%-*s | %-*s | %-*s" % (self.artistMaxLen, artist, self.albumMaxLen, album, self.titleMaxLen, title)


