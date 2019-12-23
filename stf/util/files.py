import os

def getNameFromPath(path):
    return os.path.split(os.path.splitext(path)[0])[-1]
