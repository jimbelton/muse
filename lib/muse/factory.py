#!/usr/bin/python

import filecmp
import os
import re
#import sys
from muse.Mp3File import Mp3File

extPattern = re.compile(r'.+\.(.+)$')

def createAudioFile(filePath, options):
    match = extPattern.match(filePath)
    
    if not match:
        return None
        
    ext = match.group(1)
    
    if ext == "mp3":
        return Mp3File(filePath, options)
    else:
        return None
