#!/usr/bin/python

import filecmp
import os
import re

from muse.AudioFile import AudioFile
from muse.Mp3File   import Mp3File

extensionPattern  = re.compile(r'.+\.(.+)$')
ignoredExtensions = dict.fromkeys(["cue", "db", "gif", "ini", "log", "jpeg", "jpg", "part", "pl", "txt"])
audioExtensions   = dict.fromkeys(["flac", "m3u", "m4a", "ogg", "wma"])

def createAudioFile(filePath, options = {}):
    match = extensionPattern.match(filePath)
    
    if not match:
        return None
        
    ext = match.group(1).lower()
        
    if ext == "mp3":
        return Mp3File(filePath, options)
    
    if ext in audioExtensions:
        return AudioFile(filePath, options)
        
    if ext in ignoredExtensions:
        return None
        
    print "muse.createAudioFile: warning: Ignoring unknown file extension '%s' in file %s" % (ext, filePath)
    ignoredExtensions[ext] = filePath
    return None
