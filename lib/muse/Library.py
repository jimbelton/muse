import os
import shutil
import sys

from muse.Factory import createAudioFile
from muse.Mp3File import Mp3FileError
from muse.Options import info, options, warn, takeAction

class Library:
    def __init__(self, library, subdir = ".", artistRe = None, albumRe = None, titleRe = None):
        self.files        = {}    # Songs indexed by filename
        self.audioMd5s    = {}    # Songs indexed by MD5
        self.sizes        = {}    # Lists of songs, indexed by size (only until audio MD5s are generated)
        self.artists      = {}
        self.artistMaxLen = len("Artist or Group")
        self.albumMaxLen  = len("Album")
        self.titleMaxLen  = len("Song")
        self.library      = os.path.abspath(library)    # Pass this single reference to all songs to conserve memory

        curDir = os.getcwd()
        os.chdir(library)    # Keep paths short

        for dirPath, subDirs, dirFiles in os.walk(subdir):
            for file in dirFiles:
                filePath  = dirPath + "/" + file

                try:
                    audioFile = createAudioFile(filePath, rootPath=library)

                    if not audioFile:
                        continue

                    key           = file.lower()    # The lower case file name must be a unique key in the library
                    audioFile.key = key

                    # Only check like sized files for dups while constructing if run in 'fix' mode (slows loading a lot)
                    #
                    if options['fix']:
                        other         = self.findSong(audioFile)

                        if other:
                            warn("Ignoring file %s because its audio is identical to %s" % (filePath, other.filePath))
                            continue

                    if key in self.files:
                        warn("Ignoring file %s because it's name duplicates %s" % (filePath, self.files[key].filePath))
                        continue

                    self.files[key]  = audioFile
                    size             = audioFile.getSize()
                    self.sizes[size] = self.sizes[size] if size in self.sizes else []
                    self.sizes[size].append(audioFile)

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
                return other

            else:
                warn("File %s has the same name as %s but has different audio" % (song.getPath(), other.getPath()))

        size = song.getSize()

        if size in self.sizes:
            audioMd5 = song.getAudioMd5()

            if audioMd5 in self.audioMd5s:
                return self.audioMd5[audioMd5]

            sizeList = self.sizes[size]

            while len(sizeList) > 0:
                other                         = sizeList.pop()
                otherAudioMd5                 = other.getAudioMd5()
                self.audioMd5s[otherAudioMd5] = other

                if audioMd5 == otherAudioMd5:
                    return other

        return None

    def newSongsInOther(self, other, artist, album=None, title=None, command='compare'):
        for album in (album,) if album else self.artists[artist]['albums']:
            for title in (title,) if title else self.artists[artist]['albums'][album]['songs']:
                song      = self.artists[artist]['albums'][album]['songs'][title]
                otherSong = other.findSong(song)

                if otherSong:
                    if song.compare(otherSong):
                        if options['fix'] and takeAction("move %s to %s" % (otherSong.getPath(), otherSong.getPath(song.filePath))):
                            otherSong.move(song.filePath)    # Relies on filePath being the relative path
                            song.syncModTime(otherSong)
                            return

                    info("Song %s has the same audio as song %s" %(song.getPath(), otherSong.getPath()));

                elif command == "backup" or command == "restore":
                    otherPath = os.path.join(other.library, song.filePath)

                    if takeAction("%s %s to %s" % (command, song.getPath(), otherPath)):
                        song.copy(otherPath)
                        #other.addSong(otherPath)    # Need to factor this function

    def diff(self, backup, command='compare'):
        libArtists = self.getArtists()
        bakArtists = backup.getArtists()

        while len(libArtists) > 0 or len(bakArtists) > 0:
            if len(bakArtists) == 0 or (len(libArtists) >0 and libArtists[-1] > bakArtists[-1]):
                artist = libArtists.pop()
                info("Library artist %s not found in backup" % artist)
                self.newSongsInOther(backup, artist, command=command)
                continue

            if len(libArtists) == 0 or (len(bakArtists) > 0 and bakArtists[-1] > libArtists[-1]):
                artist = bakArtists.pop()
                info("Backup artist %s not found in library" % artist)
                continue

            artist = libArtists.pop()
            bakArtists.pop()
            libAlbums = self.getAlbums(artist)
            bakAlbums = backup.getAlbums(artist)

            while len(libAlbums) > 0 or len(bakAlbums) > 0:
                if len(bakAlbums) == 0 or (len(libAlbums) > 0 and libAlbums[-1] > bakAlbums[-1]):
                    album = libAlbums.pop()
                    info("Library artist %s album %s not found in backup" % (artist, album))
                    self.newSongsInOther(backup, artist, album, command=command)
                    continue

                if len(libAlbums) == 0 or (len(bakAlbums) > 0 and bakAlbums[-1] > libAlbums[-1]):
                    album = bakAlbums.pop()
                    info("Backup artist %s album %s not found in library" % (artist, album))
                    continue

                album = libAlbums.pop()
                bakAlbums.pop()
                libTitles = self.getTitles(artist, album)
                bakTitles = backup.getTitles(artist, album)

                while len(libTitles) > 0 or len(bakTitles) > 0:
                    if len(bakTitles) == 0 or (len(libTitles) > 0 and libTitles[-1] > bakTitles[-1]):
                        title = libTitles.pop()
                        info("Library artist %s album %s title %s not found in backup" % (artist, album, title))
                        self.newSongsInOther(backup, artist, album, title, command=command)
                        continue

                    if len(libTitles) == 0 or (len(bakTitles) > 0 and bakTitles[-1] > libTitles[-1]):
                        title = bakTitles.pop()
                        info("Backup artist %s album %s title %s not found in library" % (artist, album, title))
                        continue

                    libTitles.pop()
                    bakTitles.pop()

    def display(self):
        print "%-*s | %-*s | %-*s" % (self.artistMaxLen, "Artist or Group", self.albumMaxLen, "Album", self.titleMaxLen, "Title")
        print "%s-+-%s-+-%s" % (self.artistMaxLen * "-", self.albumMaxLen * "-", self.titleMaxLen * "-")

        for artist in self.getArtists():
            for album in self.getAlbums(artist):
                for title in self.getTitles(artist, album):
                    print "%-*s | %-*s | %-*s" % (self.artistMaxLen, artist, self.albumMaxLen, album, self.titleMaxLen, title)
