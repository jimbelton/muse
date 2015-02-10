import filecmp
import os
import re

from muse.AudioFile import AudioFile
from muse.Mp3File   import Mp3File
from muse.Options   import warn

extensionPattern  = re.compile(r'.+\.(.+)$')
ignoredExtensions = {"cue", "db", "gif", "ini", "log", "jpeg", "jpg", "m3u", "part", "pl", "png", "sfv", "txt"}
audioExtensions   = {"flac", "m4a", "ogg", "wma"}

def createAudioFile(filePath, rootPath=None):
    match = extensionPattern.match(filePath)

    if not match:
        return None

    ext = match.group(1).lower()

    if ext == "mp3":
        return Mp3File(filePath, rootPath)

    if ext in audioExtensions:
        return AudioFile(filePath, rootPath)

    if ext in ignoredExtensions:
        return None

    warn("muse.createAudioFile: warning: Ignoring unknown file extension '%s' in file %s" % (ext, filePath))
    ignoredExtensions.add(ext)
    return None
