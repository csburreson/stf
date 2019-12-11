import json
from os.path import join

import openhtf as htf
from openhtf import measures, Measurement
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.util.checkpoints import checkpoint as CHECKPOINT

# first is for local dev setup 
from .tools.python.iceboot import iceboot_session_cmd
from . import db

import stf

from .util.colors import termcolor as clr


FRAMEWORK_VERSION = '0.2'
# aliases
M = Measurement
STOP = htf.PhaseResult.STOP
CONTINUE = htf.PhaseResult.CONTINUE
REPEAT = htf.PhaseResult.REPEAT
FAIL = htf.PhaseResult.FAIL_AND_CONTINUE
options = htf.PhaseOptions

# defined in __init__
global DB_DIR
ParamDB = None

### JSON output stuff
# move to output lib file
OUTPUT_DIR = 'results/'
OUTPUT_FMT_STRING = '{metadata[type]}.{dut_id}.{metadata[test_name]}-v{metadata[test_version]}.json'
OUTPUT_JSONFILE = '{}{}'.format(OUTPUT_DIR, OUTPUT_FMT_STRING)

### fake DB stuff
DEVICES = []
META = {}

### dev symbols
import os
class DEBUG:
    LOG = os.environ.get('STF_DEBUG', False)
    # create "fake" iceboot 
    FAKE_ICEBOOT = os.environ.get('STF_FAKEICEBOOT', False)
    # skip loading of FW file
    SKIP_FW = os.environ.get('STF_SKIPFW', False)
    


def dbg(s, trace=5):
    if DEBUG.LOG:
        import inspect
        caller = []
        for x in range(1, trace):
            try:
                frame = inspect.stack()[x]
                caller.append(frame[3])
            except IndexError:
                pass
        caller = reversed(caller)
        trace = ' -> '.join(caller) if caller else 'n/a'
        print('{} {} {}'.format(
            clr('DEBUG >>', 'red'),
            clr(trace, 'gray'),
            clr(s, 'aqua')
        ))
debug = dbg

class FakeIceboot(object):
    '''
    placeholder class for development which accepts any method call
    and returns nothing
    '''
    def __init__(self, *args, **kw):
        stf.dbg('Creating FAKE iceboot class with (unused) kwargs: {}'.format(kw))

    def __getattr__(self, attr):
        def fake(*args, **kw):
            pass
        if attr == 'fpgaVersion':
            return lambda: 0x6a
        return fake

def getIcebootSession(fake=False, **kw):
    if fake:
        return FakeIceboot()

    class IcebootOpts:
        host = '192.168.0.10'
        port = 5012
        debug = True
        fpgaConfigurationFile = None
        test = []


    dbg('(framework) Starting iceboot session ...')
    if kw:
        dbg('(framework) using overrides: {}'.format(json.dumps(kw)))
    return iceboot_session_cmd.init(IcebootOpts, **kw)


def getDevices(device_type=None):
    '''
    pretend to be a db interface...
    '''
    global DEVICES
    global META 
    devices = join(stf.env.DB_DIR, 'all.json')
    if not DEVICES:
        with open(devices, 'r') as f:
            DB = json.load(f)
        DEVICES = DB['devices']
        META = DB['meta']

    if (device_type):
        return [d for d in DEVICES if d["type"] == device_type]
    return DEVICES
        

# test running code 

def run():
    '''
    run should discover devices (TODO) and loop over and run all registered
    tests
    '''
    mainboard = getDevices('mainboard')
    device = mainboard[0]
    ran = False
    for testClass in stf.TESTABLE_CLASSES:
        dbg("Running {}".format(testClass.test_name))

        if _run(testClass, device):
            ran = True

    if not ran:
        #findAndRun()
        dbg('Nothing ran :(')
        pass

def _run(testClass, device):
      #if not check_attrs(testClass, required=False):
      #    dbg('Warn: {} is missing attributes'.format(testClass.__name__))
      #    return False

      testClass.execute(device)
      return True
