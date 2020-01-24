import os
import glob

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

def globFiles(*dirs, pattern='*'):
    gp = list(dirs) + [pattern]
    path = os.path.join(*gp)
    return glob.glob(path)

def getFileSize(path):
    stat = os.stat(path)
    return stat.st_size

def getFilePath(path):
    '''
    tries to get "path" whether relative to framework or not
    '''
    from stf import config

    locations = [
        '.',
        config.settings.paths.testconfig,
        config.settings.paths.stf_home,
    ]

    for loc in locations:
        p = os.path.join(loc, path)
        if os.path.exists(p):
            return os.path.abspath(p)
    return None
        
join = os.path.join
exists = os.path.exists
