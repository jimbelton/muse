import filecmp
import os
import re

numericPattern = re.compile(r'(\d+)\s*(.*)$')
articlePattern = re.compile(r'(?:(?:a|an|the) )?(.+)')

def simpleString(string):
    '''trim leading and trailing space, replace runs of whitespace with single spaces, lower case and remove leading article'''

    return articlePattern.match(" ".join(string.split()).lower()).group(1) if string else None

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
