from .colors import termcolor as clr
from stf import _PRINT
from stf.util.files import getFileSize
import stf

def flatten(d, separator='.'):
  final = {}
  def _flatten_dict(obj, parent_keys=[]):
    for k, v in obj.items():
      if isinstance(v, dict):
        _flatten_dict(v, parent_keys + [k])
      else:
        key = separator.join(parent_keys + [k])
        final[key] = v
  _flatten_dict(d)
  return final


class JsObject(object):
    def __init__(self, *args, **kwargs):
        for arg in args:
            self.__dict__.update(arg)
        
        self.__dict__.update(kwargs)
    
    def __getitem__(self, name):
        return self.__dict__.get(name, None)
    
    def __setitem__(self, name, val):
        return self.__dict__.__setitem__(name, val)

    def __delitem__(self, name):
        if self.__dict__.has_key(name):
            del self.__dict__[name]
    
    def __getattr__(self, name):
        return self.__getitem__(name)
        
    def __setattr__(self, name, val):
        return self.__setitem__(name, val)
      
    def __delattr__(self, name):
        return self.__delitem__(name)
        
    def __iter__(self):
        return self.__dict__.__iter__()
      
    def __repr__(self):
        return self.__dict__.__repr__()
  
    def __str__(self):
        return self.__dict__.__str__()

    def __eq__(self, other):
        return self.__dict__ == other

    def get(self, *a, **k):
        return self.__dict__.get(*a, **k)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def dict(self):
        return self.__dict__

def jsonify(d):
  def _recurse_dict(obj, parent_keys=[]):
    jobj = JsObject()
    if not isinstance(obj, (dict, list)):
        return obj
    for k, v in obj.items():
      if isinstance(v, dict):
        jobj[k] = _recurse_dict(v)
      elif isinstance(v, list):
        jobj[k] = [_recurse_dict(x) for x in v]
      else:
        jobj[k] = v
    return jobj
      
  return _recurse_dict(d)

__SHOW_GROUPS = []
def setInfoGroups(gs):
    global __SHOW_GROUPS
    __SHOW_GROUPS = gs

def get_InfoWithGroups(groups):
    def wrap(s):
        INFO(s, groups=groups)
    return wrap

def INFO(s, **kw):
    groups = kw.get('groups', [])
    if groups and __SHOW_GROUPS:
        if not (set(groups) & set(__SHOW_GROUPS)):
            return
    _PRINT(clr('INFO >>> ', 'gray') + clr(s, 'gold'))


def check_mainboard_fwfile(flash):
    '''
    check whether mainboard file is present and configured
    '''
    fname = stf.config.settings.paths.fwfile
    fwvnum = stf.config.settings.iceboot.fw_version
    fsize = getFileSize(fname)

    stf.debug(f'Checking flash for name={fname} size={fsize}...')
    for doc in flash:
        if not ('Name' in doc and 'Size' in doc):
            continue
        stf.debug(f"  name={doc['Name']}, size={doc['Size']}")
        if fwvnum in doc['Name']:
            if doc['Size'] == str(fsize):
                stf.debug(f"  found correct version with correct fsize (rv=ok)")
                return 'ok'
            else:
                stf.debug(f"  found correct version, but BAD fsize (rv=corrupt)")
                return 'corrupt'

    stf.debug(f"FW File not present in flash! (rv=missing)")
    return 'missing'
