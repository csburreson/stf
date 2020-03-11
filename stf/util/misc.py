from copy import deepcopy
from .colors import termcolor as clr
from stf import _PRINT
from stf.util.files import getFileSize
from stf.util import exceptions
import stf
import uuid
from datetime import datetime # XXX: move to util.time
import time


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

    def __deepcopy__(self, memo=None):
        return JsObject(deepcopy(self.__dict__, memo=memo)).dict()

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


# decorator to try a fn a couple times and sleep between, accepts 
def try_repeat(repeat_limit=3, sleep=1, msg=None, exc_cls=(UnicodeDecodeError), 
               fail_exception=exceptions.STFRefuseToRun):
    '''
    decorator to try a fn up to `repeat_limit` times with a sleep=`sleep` wait
    
    accepts `exc_cls` which is a TUPLE (important! not a list) of 
    classes to except on and go ahead with retry
    
    optional msg will be printed to stf.debug if provided
    '''
    def actual_decorator(try_fn):
        def wrap(*args, **kw):
            # nonlocal so wrap fn can crawl up scope-chain to modify 
            # repeat_limit
            nonlocal repeat_limit
            while repeat_limit:
                try:
                    return try_fn(*args, **kw)
                except exc_cls as e:
                    repeat_limit -= 1
                    stf.debug(f'Exception: {e}; trying again after {sleep}s')
                    if msg:
                        stf.debug(msg)
                    if sleep:
                        time.sleep(sleep)
            if fail_exception:
                raise fail_exception(f'Failed to execute {try_fn.__name__}')
        return wrap
    return actual_decorator


def check_mainboard_fwfile(flash):
    '''
    check whether mainboard file is present and the proper size

    can return 'ok', 'corrupt', 'missing' or 'skip'
    '''
    fname = stf.config.settings.paths.fwfile
    fwvnum = stf.config.settings.iceboot.fw_version
    if stf.config.DEBUG.SKIP_FW:
        stf.debug(f'[SKIPPED] Checking flash for name={fname}')
        return 'skip'
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



def getUUID():
    return uuid.uuid1()


def get_run_args():
    import openhtf
    import argparse
    from openhtf.util.argv import ModuleParser
    ap = ModuleParser()

    #ap = argparse.ArgumentParser()

    # optional: set off key=value pairs to insert into metadata
    ap.add_argument('--meta', default=None, 
        nargs=argparse.REMAINDER)
    # optional: path to JSON file adding metadata
    ap.add_argument('--metafile', default=None, 
        nargs=1)
    ap.add_argument('--testconfig', default=None,
        nargs=1)

    args = ap.parse_known_args()
    stf.debug(f"args: {args}")
    return args[0]

def get_runset_args():
    import openhtf
    import argparse
    from openhtf.util.argv import ModuleParser
    CFG = stf.util.config.get_config()
    cfg_conn = CFG.getIcebootOpts()
    ap = ModuleParser()
    p = argparse.ArgumentParser(prog='runset')
    p.add_argument('set_name', type=str, nargs='?')
    p.add_argument('--iceboot_host', '--host', '-H', type=str, default=cfg_conn.host)
    p.add_argument('--iceboot_port', '--port', '-P', type=str, default=cfg_conn.port)
    p.add_argument('--iceboot_debug', '-D', action='store_true', default=cfg_conn.debug)
    args = p.parse_known_args()
    return args[0]

    args = p.parse_args()
     
