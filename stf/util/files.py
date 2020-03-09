import os
import glob
import pathlib

def popPath(path):
    
    x, y = os.path.split(path)
    # if it's a filename or doesn't have a trailing slash
    if y:
        return x, y
    
    # otherwise pop the directory
    return os.path.split(x)


'''
def ensureEmptyDir(path=None, delete_pattern='*', root=None, dirs=[]):
    if root:

        return ensureEmptyDir(
def _ensureEmptyDir(path, delete_pattern='*'):

def _ensureEmptyDir(path, delete_pattern='*'):
    if path == '/':
        raise Exception('Unable to ensure "/" is empty')

    _path = path
    ds = []
    import stf
    while not os.path.exists(_path):
        
        root, d = popPath(_path)
        stf.debug(f'foo:  {_path}, {root}, {d}')
        if os.path.exists(root):
            os.mkdir(_path)
            break
        _path = root
        ds.append(d)

        from stf import config
        if not config.paths.stf_home in root:
            # XXX: STFPathException
            raise Exception(f'Cannot find root direcotry for {d} (tried: {root})')
    if ds:
        for d in ds:
            _path = os.path.join(_path, d)
            os.mkdir(d)
    else:
        os.mkdir(_path)
        
    # purge files
    remove_files(path, delete_pattern)
'''

def remove_files(path, pattern):
    files = globFiles(path, pattern)

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

def getFilePath(*path_, filename=None):
    '''
    tries to get "path" whether relative to framework or not
    '''
    from stf import config
    path = os.path.join(*path_)

    locations = [
        '.',
        config.settings.paths.testconfig,
        config.settings.paths.stf_home,
    ]

    for loc in locations:
        p = os.path.join(loc, path)
        if os.path.exists(p):
            if filename:
                p = os.path.join(p, filename)
            return os.path.abspath(p)
    return None

def getDirs(path):
    # trim 0th dir 
    return [x[0] for x in os.walk(path)][1:]


# XXX: make sure root exists and is within home?
def mkdir(*path):
    try:
        os.makedirs(os.path.join(*path))
    except FileExistsError:
        pass
    finally:
        return os.path.join(*path)
        
join = os.path.join
exists = os.path.exists
Path = pathlib.Path
