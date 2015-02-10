import filecmp
import os
import re
import string
import sys

articlePattern = re.compile(r'(?:(?:a|an|the) )?(.+?)(?:, (?:a|an|the))?$')
latinToAscii   = {ord('\xD6'): u"O", ord('\xF6'): u"o"}

def simpleString(string):
    '''trim leading and trailing space, replace whitespaces with single spaces, lower case and remove leading/trailing article'''
    if string == None:
        return None

    alreadyUnicode = isinstance(string, unicode)

    if not alreadyUnicode:
        string = string.decode('utf8')

    string = string.translate(latinToAscii)

    if alreadyUnicode:
        return articlePattern.match(u' '.join(string.split()).lower()).group(1).replace(" & ", " and ").replace(", and ", " and ")

    match = articlePattern.match(' '.join(string.encode('utf8').split()).lower())
    return match.group(1).replace(" & ", " and ").replace(", and ", " and ")

def reconcileStrings(*strings, **options):
    '''if all simplified strings are the same, returns the first string, unsimplified;
       if no strings are passed, returns the default, or None if the default keyword argument wasn't passed
       if at least one simplified string doesn't match the others, returns None
    '''

    first  = None

    for string in strings:
        if not string:
            continue

        if first == None:
            first  = string
            simple = None
            continue

        if simple == None:
            simple =simpleString(first)

        if simple != simpleString(string):
            return None

    return first if first else options['default'] if 'default' in options else None

def safeAppend(head, tail, suppress=None):
    if not head or (suppress and head == suppress):
        return ""

    return head + tail
