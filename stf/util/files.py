import os
import glob

def popPath(path):
    
    x, y = os.path.split(path)
    # if it's a filename or doesn't have a trailing slash
    if y:
        return x, y
    
    # otherwise pop the directory
    return os.path.split(x)

def ensureEmptyDir(path, delete_pattern='*'):
    if path == '/':
        raise Exception('Unable to ensure "/" is empty')

    if not os.path.exists(path):
        root, d = popPath(path)
        if not os.path.exists(root):
            # XXX: STFPathException
            raise Exception(f'Cannot find root direcotry for {d} (tried: {root})')

        os.mkdir(path)
        
    else:
        files = globFiles(path, pattern=delete_pattern)

        for f in files:
            try:
                os.remove(f)
            except Exception as e:
                stf.debug(str(e))


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
    import stf
    stf.debug(f'dirs={dirs}')
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
