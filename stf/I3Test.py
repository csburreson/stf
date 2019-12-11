'''
This is the core file for the testing api

the test designers should not need to read this

TODO: create module and make this "core" with "Test.Test" (mod.class) an alias for <mod>/core.py:Test
'''
import json
from os.path import join

import openhtf as htf
from openhtf import measures, Measurement
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.util.checkpoints import checkpoint as CHECKPOINT

from iceboot import iceboot_session_cmd
import db

from util.colors import termcolor as clr



FRAMEWORK_VERSION = '0.2'
# aliases
M = Measurement
STOP = htf.PhaseResult.STOP
CONTINUE = htf.PhaseResult.CONTINUE
REPEAT = htf.PhaseResult.REPEAT
FAIL = htf.PhaseResult.FAIL_AND_CONTINUE
options = htf.PhaseOptions

DB_DIR = 'data/'
ParamDB = None

REQUIRED_ATTRS = ['VERSION', 'TESTS']

# allows @Test.test decorator
def test(f):
    @htf.TestPhase()
    def deco(*args, **kw):
        return f(*args, **kw)
    # preserve original test name
    deco.func.__name__ = f.__name__
    deco.options.name = f.__name__
    return deco

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
  
# XXX: this is gotten from the "database" ;)
def get_db():
    global ParamDB
    if not ParamDB:
        ParamDB = db.getParamDB()
    return ParamDB



### MAIN CODE


def getIcebootSession(fake=False, **kw):
    if not fake:
        # TODO: fix iceboot config opts
        # XXX: can't use optparse with argparse :(
        class IcebootOpts:
            host = '192.168.0.10'
            port = 5012
            debug = True
            fpgaConfigurationFile = 'fw_0x6a.rbf'
            test = []

        dbg('(framework) Starting iceboot session ...')
        if kw:
            dbg('(framework) using overrides: {}'.format(json.dumps(kw)))
        return iceboot_session_cmd.init(IcebootOpts, **kw)

    dbg('(framework) Starting FAKE iceboot session')
    class Iceboot:
        def __init__(self, **kw):
            self.status = 'OK' if not 'status' in kw else 'Error'
            self.wait = 0

        def __repr__(self):
            return 'iceboot'
        __str__ = __repr__

        def fpgaWrite(self, *args):
            pass

        def fpgaVersion(self):
            return 0x6a

        def cmd(self, x):
            if x == 'funkItUp':
                self.status='Error'
            if x == 'wait':
                print "XXX: iceboot: waiting 2s"
                import time
                time.sleep(2)
                self.wait += 1
                if self.wait == 3:
                    return 'OK'
                return 'Not ok'

            return self.status
        #def __call__:
        #  return 'OK'
    return Iceboot()

def getDevices(device_type=None):
    '''
    pretend to be a db interface...
    '''
    global DEVICES
    global META 
    devices = join(DB_DIR, 'all.json')
    if not DEVICES:
        with open(devices, 'r') as f:
            DB = json.load(f)
        DEVICES = DB['devices']
        META = DB['meta']

    if (device_type):
        return [d for d in DEVICES if d["type"] == device_type]
    return DEVICES
        
def getDeviceByType(device_type):
    return [
      d for d in DEVICES \
      if device_type == d['type']
    ]
    

def getDeviceById(device_uid):
    '''
    Are "id" fields always totally unique? or should we add 
    something like the hw type somehow?
    '''
    for d in DEVICES:
        if device_uid == d['id']:
            return d





# test running code

def check_attrs(cls, attrs=REQUIRED_ATTRS, required=True):
    try:
        for a in attrs:
            if not hasattr(cls, a):
                raise AttributeError('Missing required attribtue {}'.format(a))
    except AttributeError:
        if required:
           raise
        return False
    return True

def run():
    mainboard = getDevices('mainboard')
    device = mainboard[0]
    ran = False
    for testClass in TESTABLE_CLASSES:
        dbg("Running {}".format(testClass.__name__))

        if _run(testClass, device):
            ran = True

    if not ran:
        findAndRun()

def findAndRun(testClass=None):
    '''
    This function magically runs either one test or all in a file 
    XXX: probably we should just use the register decorator
    '''
    mainboard = getDevices('mainboard')
    device = mainboard[0]

    if testClass:
        testClasses = [testClass]
    else:
        # get class methods
        # 
        import inspect
        frame = inspect.stack()[2]
        mod = inspect.getmodule(frame[0])


        # XXX: for now... only allow classes with "Test" in the name
        testClasses = [getattr(mod, x) for x in dir(mod) if 'Test' in x and x != 'Test']

    ran = False
    for testClass in testClasses:
        if _run(testClass, device):
            ran = True

    if not ran:
        print 'No tests found :('

def _run(testClass, device):
      # XXX: for now, we use TESTS to determine whether to run
      # if hasattr(testClass, 'TESTS'):
      # see if this is a runnable test
      if not check_attrs(testClass, required=False):
          dbg('Warn: {} is missing attributes'.format(testClass.__name__))
          #return False

      test = testClass(
        testClass.VERSION,
        params=getattr(testClass, 'PARAMS', {}),
        config=getattr(testClass, 'CONFIG', {})
      )
      test.execute(device)
      return True

### Exceptions?

class ExitWithFail(Exception):
    pass

class ExitWithContinue(Exception):
    pass

### DECORATORS
TESTABLE_CLASSES = []
def runnable(cls):
    global TESTABLE_CLASSES
    TESTABLE_CLASSES.append(cls)
    return cls

def register(**kw):
    def wrap(cls):
        conf_file = kw.get('config_file')
        if conf_file:
            with open(conf_file, 'r') as f:
                dbg("(@configure) loaded {}".format(conf_file))
                cls._PARAMS = json.load(f)
                cls._PARAM_CONF_FILE = conf_file
                dbg("(@configure) {}".format(cls._PARAMS))
        version = kw.get('version')
        if not version and not cls.VERSION:
            raise Exception('Misconfigured test, missing version')
        cls.VERSION = version
        return runnable(cls)
    return wrap

def configure(config_file, **kw):
    '''
    this decorator is applied to a runnable I3Test
    and specifies the location of a JSON file containing
    expected parameters for the test

    in the future, this could be replaced with a database
    call using the test class name (__class__.__name__)
    and test/phase name (cls.TESTS[:].__name__) and 
    possibly the version or something to
    return a document containing the test params
    '''
    def wrap(cls):
        with open(config_file, 'r') as f:
            dbg("(@configure) loaded {}".format(config_file))
            cls._PARAMS = json.load(f)
            cls._PARAM_CONF_FILE = config_file
        return cls
    return wrap

### VALIDATORS

