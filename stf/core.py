import json
import openhtf as htf
# XXX: this monkey-patch fixes JSON serialization problems with numpy arrays in
# test.measurements
x = htf.data.convert_to_base_types
def foo(*a, **k):
  try:
    return a[0].tolist()
  except AttributeError:
    return x(*a, **k)
htf.data.convert_to_base_types = foo
# XXX end hack
from openhtf import measures, Measurement
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.util.checkpoints import checkpoint as CHECKPOINT

# first is for local dev setup 
from .tools.python.iceboot import iceboot_session_cmd
from . import db

from stf.debug import dbg, DEBUG
from stf import ENV, getRegisteredClasses, getRegisteredClassesByName, getClassContext, getRegisteredClass, _PRINT
from .parse import SetConfig
from .util.files import getNameFromPath


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
            f = kw.get('retval', '')
            if f is not None:
                if callable(f):
                    return f()
                return f
            return None
        if attr == 'fpgaVersion':
            return lambda: ENV.FIRMWARE_VERSION
        return fake

def getIcebootSession(fake=False, **kw):
    # default firmware path
    fw_file = ENV.FIRMWARE_FILE_PATH
    
    # this value can be null/None and that means DON'T send a fw file
    if 'fpgaConfigurationFile' in kw:
        # get this, eve
        fw_file = kw['fpgaConfigurationFile']
        dbg('fw_file: {}'.format(fw_file))

        ### HACK: make the comms test pass with a custom fpgaConfig file ... this relies on the 
        #   filename to contain the fw version.
        # XXX: should probably use splitext and basename from os
        fn = fw_file.split('/')[-1].split('.')[0]
        ENV.FIRMWARE_VERSION = int(fn[-4:], 16)
        dbg('setting fw version: {}'.format(ENV.FIRMWARE_VERSION))


    # SKIP_FW debug symbol overrides testconfig
    if DEBUG.SKIP_FW:
        dbg('NOT loading firmeware STF_SKIPFW is set')
        fw_file = None

    if fake:
        return FakeIceboot(**kw)

    class IcebootOpts:
        #host = '192.168.0.10'
        host = 'localhost'
        port = 5012
        debug = not ENV.ICEBOOT_DEBUG_OFF
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

def run_set(set_name=None, config_file=None, list_tests=False, list_overrides=False):
    # 
    import os
    if set_name:
       config_file = ENV.SETCONFIG_PTN.format(set_name)
       if not os.path.exists(config_file):
           raise Exception('Cannot find {}'.format(config_file))

    if not config_file:
       raise Exception('Must provide config file')

    if not set_name:
        set_name = getNameFromPath(config_file)

    #setConfig = stf.parse.json_load(config_file)
    setConfig = SetConfig(config_file, set_name)
    '''
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tests.Interlock import run_test
    from tests import Interlock
    from tests import ADCNoiseLevel
    dbg('HER HER HER')
    dbg(dir(Interlock))
    Interlock.STF_RUN_TEST()
    '''

    ### VERIFY CONFIG
    for test in setConfig.tests:
        testFile = '{}/{}.py'.format(ENV.TEST_DIR, test)
        dbg('verifying testfile {} ...'.format(testFile))
        try:
            with open(testFile) as f:
                testCode = f.read()
            exec(compile(testCode, testFile, 'exec'))
        except:
            dbg('exception when running {}'.format(testFile))
            raise
        #from .. import tests as definedTests
        #dbg(dir(definedTests[test]))
    setConfig.configure()

    
    dbg('registered_tests: {}'.format(getRegisteredClassesByName().keys())) 
    dbg(setConfig.instances)


    for test in setConfig.instances:
        testName = test['test_name']
        dbg('running: {}'.format(test['testinstance_name']))
        dbg('   with: {}'.format(test))

        if list_tests:
            _PRINT(test['testinstance_name'])
            continue
        if list_overrides:
            _PRINT(test['testinstance_name'])
            _PRINT(f"  args: {test['args']}")
            _PRINT(f"  expv: {test['expectedValues']}")
            continue
        #exec(testClass.execute, *getClassContext(name))
        #exec(*getClassContext(name))
        testFile = '{}/{}.py'.format(ENV.TEST_DIR, testName)

        testCode = open(testFile).read()
        ib_hack = f"""\nstf.set_default_iceboot("{ENV.CFG_ICEBOOT['host']}", "{ENV.CFG_ICEBOOT['port']}")"""
        code = f"""\nstf.core.run_single_test("{testName}", "{test['testinstance_name']}", "{setConfig.set_name}", {test['args']}, {test['expectedValues']})"""
        dbg(testCode + ib_hack + code)

        cc = getClassContext(testName)
        exec(compile(testCode + code, testFile, 'exec'), cc[2])


def run_single_test(name, instance, group, args, evs):
    test = getRegisteredClass(name)

    # XXX: reconfigure should use framework config settings here 
    # to erase test override settings used in development
    # or just have a hardcoded default
    test.reconfigure(instance, group, args, evs, {
        'iceboot': ENV.CFG_ICEBOOT
    })

    test.execute({'id': 'deadbeef'})
