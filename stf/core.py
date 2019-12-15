import json
import openhtf as htf
from openhtf import measures, Measurement
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.util.checkpoints import checkpoint as CHECKPOINT

# first is for local dev setup 
from .tools.python.iceboot import iceboot_session_cmd
from . import db

from stf.debug import dbg, DEBUG
from stf import ENV, getRegisteredClasses


### fake DB stuff
DEVICES = []
META = {}


class FakeIceboot(object):
    '''
    placeholder class for development which accepts any method call
    and returns nothing
    '''
    def __init__(self, *args, **kw):
        dbg('Creating FAKE iceboot class with (unused) kwargs: {}'.format(kw))

    def __getattr__(self, attr):
        def fake(*args, **kw):
            f = kw.get('retval')
            if f:
                if callable(f):
                    return f
                return lambda: f
            return None
        if attr == 'fpgaVersion':
            return lambda: ENV.FIRMWARE_VERSION
        return fake

def getIcebootSession(fake=False, **kw):
    if fake:
        return FakeIceboot(**kw)

    # default firmware path
    fw_file = ENV.FIRMWARE_FILE_PATH
    
    # this value can be null/None and that means DON'T send a fw file
    if 'fpgaConfigurationFile' in kw:
        # get this, eve
        fw_file = kw['fpgaConfigurationFile']

    # SKIP_FW debug symbol overrides testconfig
    if DEBUG.SKIP_FW:
        fw_file = None

    class IcebootOpts:
        #host = '192.168.0.10'
        host = 'localhost'
        port = 5012
        debug = True
        # always make this None for now, and override with testconfig
        # "Defaults" and overide THAT with testconfig "config.iceboot"
        # if provided by test writer
        fpgaConfigurationFile = fw_file
        test = []


    dbg('(framework) Starting iceboot session ...')
    if kw:
        dbg('  using overrides: {}'.format(json.dumps(kw)))
    if fw_file is None:
        dbg('  NOT sending Firmware file')
    return iceboot_session_cmd.init(IcebootOpts, **kw)


def getDevices(device_type=None):
    '''
    pretend to be a db interface...
    '''
    global DEVICES
    global META 
    if not DEVICES:
        with open(ENV.DEVICES_JSON_FILE, 'r') as f:
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
    for testClass in getRegisteredClasses():
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
