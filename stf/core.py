import json
import time
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
from stf import getRegisteredClasses, getRegisteredClassesByName, getClassContext, getRegisteredClass, _PRINT, delClassContext, INFO, ginfo 
from .parse import SetConfig
from .util import files 
from .util.colors import termcolor as tc
from .util.config import get_config

CONFIG = get_config()


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
        self.FAKE = True

    def __getattr__(self, attr):
        def fake(*args, **kw):
            f = kw.get('retval', '')
            if f is not None:
                if callable(f):
                    return f()
                return f
            return None
        if attr == 'fpgaVersion':
            return lambda: int(CONFIG.settings.iceboot.fw_version, 16)
        return fake

def getIcebootSession(**kw):
    if DEBUG.FAKE_ICEBOOT:
        return FakeIceboot(**kw)

    class IcebootOpts:
        host = CONFIG.settings.iceboot.host
        port = CONFIG.settings.iceboot.port
        debug = CONFIG.settings.iceboot.debug
        fpgaConfigurationFile = None

    dbg('Starting iceboot session ...')
    dbg(f'  {CONFIG.settings.iceboot}')
    session = None
    fail_count = 0
    while session is None and fail_count < 5:
        del session
        try:
            # this sleep prevents OSError from being thrown in some
            # circumstances
            time.sleep(1)
            session = iceboot_session_cmd.init(IcebootOpts, **kw)
        except (IOError, OSError):
            # this except doesn't seem to trigger anymore with the sleep, but
            # just in case...
            fail_count += 1
            dbg("OSERROR!!!")
            session = None
            if fail_count == 5:
                raise

    return session


def getDevices(device_type=None):
    '''
    pretend to be a db interface...
    '''
    global DEVICES
    global META 
    if not DEVICES:
        fname = CONFIG.get_path('data', CONFIG.settings.device.source)
        with open(fname, 'r') as f:
            DB = json.load(f)
        DEVICES = DB['devices']
        META = DB['meta']

    if device_type:
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
        testClass.execute(device)
        ran = True

    if not ran:
        dbg('Nothing ran :(')
        pass

def _run(testClass, device):
      return True

def run_set(set_name=None, config_file=None, list_tests=False, list_overrides=False):
    if set_name:
       config_file = CONFIG.get_path('setconfig', filename=f'{set_name}.json')
       if not files.exists(config_file):
           raise Exception('Cannot find {}'.format(config_file))

    if not config_file:
       raise Exception('Must provide config file or set name')

    if not set_name:
        set_name = files.getNameFromPath(config_file)

    setConfig = SetConfig(config_file, set_name)
    '''
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tests.Interlock import run_test
    from tests import Interlock
    from tests import ADCNoiseLevel
    dbg(dir(Interlock))
    Interlock.STF_RUN_TEST()
    '''

    ### VERIFY CONFIG
    for test in setConfig.tests:
        d = CONFIG.get_path('tests')
        testFile = f'{d}/{test}.py'
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
    
    #dbg('registered_tests: {}'.format(getRegisteredClassesByName().keys())) 
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
            _PRINT('')
            continue

        testFile = CONFIG.get_path('tests', filename=f'{testName}.py')

        testCode = open(testFile).read()
        code = f"""\nstf.core.run_single_test("{testName}", "{test['testinstance_name']}", "{setConfig.set_name}", {test['args']}, {test['expectedValues']})"""

        cc = getClassContext(testName)
        exec(compile(testCode + code, testFile, 'exec'), cc[2])


def run_single_test(name, instance, group, args, evs):
    test = getRegisteredClass(name)
    cName = tc(name, 'aqua')
    cInst = tc(instance, 'aqua')

    INFO(f'Running {cName}:{cInst}', groups=['runset', 'framework'])

    # iceboot settings no longer provided here?
    test.reconfigure(instance, group, args, evs, {})

    # XXX: multiple devices
    test.execute({'id': 'deadbeef'})
