import filecmp
import os
import re

from muse.AudioFile import AudioFile
from muse.Mp3File   import Mp3File

extensionPattern  = re.compile(r'.+\.(.+)$')
ignoredExtensions = {"cue", "db", "gif", "ini", "log", "jpeg", "jpg", "part", "pl", "txt"}
audioExtensions   = {"flac", "m3u", "m4a", "ogg", "wma"}

def createAudioFile(filePath):
    match = extensionPattern.match(filePath)

    if not match:
        return None

    ext = match.group(1).lower()

    if ext == "mp3":
        return Mp3File(filePath)

    if ext in audioExtensions:
        return AudioFile(filePath)

    if ext in ignoredExtensions:
        return None

    sys.stderr.writer("muse.createAudioFile: warning: Ignoring unknown file extension '%s' in file %s" % (ext, filePath))
    ignoredExtensions.add(ext)
    return None
