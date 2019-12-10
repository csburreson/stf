import json
from os.path import join

import openhtf as htf
from openhtf import measures, Measurement
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.util.checkpoints import checkpoint as CHECKPOINT

# first is for local dev setup 
try:
    from .iceboot import iceboot_session_cmd
except ModuleNotFoundError:
    from iceboot import iceboot_session_cmd
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
DEBUG = os.environ.get('I3TEST_DEBUG', False)
# create "fake" iceboot 
FAKE_ICEBOOT = os.environ.get('FAKE_ICEBOOT', False)


def dbg(s, trace=5):
    if DEBUG:
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



def getIcebootSession(fake=False, **kw):
    class IcebootOpts:
        host = '192.168.0.10'
        port = 5012
        debug = True
        #fpgaConfigurationFile = join(stf.ENV.DATA_DIR, 'fw_0x6a.rbf')
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
      # XXX: for now, we use TESTS to determine whether to run
      # if hasattr(testClass, 'TESTS'):
      # see if this is a runnable test
      #if not check_attrs(testClass, required=False):
      #    dbg('Warn: {} is missing attributes'.format(testClass.__name__))
          #return False

      testClass.execute(device)
      return True
