import os
import sys

from muse.Factory import createAudioFile
from muse.Mp3File import Mp3FileError
from muse.Options import info, options, warn, takeAction

class Library:
    def __init__(self, library, subdir = ".", artistRe = None, albumRe = None, titleRe = None):
        self.files        = {}
        self.sizes        = {}
        self.artists      = {}
        self.artistMaxLen = len("Artist or Group")
        self.albumMaxLen  = len("Album")
        self.titleMaxLen  = len("Song")

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

            if song.compareAudio(other):
                info("File %s has the same audio content as %s" % (song.getPath(), other.getPath()))
                return other

            else:
                warn("File %s has the same name as %s but has different audio" % (song.getPath(), other.getPath()))

            return None

    def newSongsInOther(self, other, artist, album=None, title=None, command='compare'):
        for album in (album) if album else self.artists[artist]['albums']:
            for title in (title) if title else self.artists[artist]['albums'][album]['songs']:
                song      = self.artists[artist]['albums'][album]['songs'][title]
                otherSong = other.findSong(song)

                if otherSong and options['fix']:
                    if song.compare(otherSong):
                        if takeAction("move %s to %s" % (otherSong.getPath(), otherSong.getPath(song.filePath))):
                            otherSong.move(song.filePath)    # Relies on filePath being the relative path
                            song.syncModTime(otherSong)

    def diff(self, backup, command='compare'):
        libArtists = self.getArtists()
        bakArtists = backup.getArtists()

        while len(libArtists) > 0 or len(bakArtists) > 0:
            if len(bakArtists) == 0 or libArtists[-1] > bakArtists[-1]:
                artist = libArtists.pop()
                print "Library artist " + artist + " not found in backup"
                self.newSongsInOther(backup, artist, command=command)
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


