import sys

options = {}

def getOption(name, default = None):
    if name in options:
        return options[name]

    return default

def takeAction(action):
    if getOption('noaction', False):
        print "Would " + action
        return False

    if getOption('verbose', False):
        print "Will now " + action

    return True

def formatMessage(type, message, file, line):
    output = [message, ": "]

    if file:
        output.append(file)

        if line:
            output.extend(["(", str(line), ")"])

        output.append(": ")

    output.append(message)

    if not message.endswith("\n"):
        output.append("\n")

    return "".join(output)

def warn(message, file = None, line = None):
    if getOption('warning', False):
        return

    sys.stderr.write(formatMessage("warning", message, file, line))

    if getOption('fail-on-warning', False):
        sys.exit(1)

def error(message, file = None, line = None):
    sys.stderr.write(formatMessage("error", message, file, line))

    if not getOption('ignore-errors', False):
        sys.exit(1)
