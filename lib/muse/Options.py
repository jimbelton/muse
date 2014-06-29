options = {}

def getOption(name, default = None):
    if name in options:
        return options[name]
    
    if default:
        return default
        
    return None
