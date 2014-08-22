import filecmp
import os
import re

def simpleString(string):
    return " ".join(string.split()).lower() if string != None else None
