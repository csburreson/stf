import os

def getNameFromPath(path):
    return os.path.split(os.path.splitext(path)[0])[-1]

def getFWVersionFromFile(path):
    '''
    e.g.
        path = 'fw_0xb0.rbf'
        path = 'awd/awd/awd/daw/degg_test_0xb0.rbf'

    '''
    x = getNameFromPath(path)
    version = x.split('_')[-1]

    return version

join = os.path.join
exists = os.path.exists
