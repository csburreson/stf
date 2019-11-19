'''
This is the core file for the testing api

the test designers should not need to read this

TODO: create module and make this "core" with "Test.Test" (mod.class) an alias for <mod>/core.py:Test
'''

import openhtf as htf
from openhtf import measures, Measurement
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.util.checkpoints import checkpoint as CHECKPOINT
from iceboot import iceboot_session_cmd

import json



### move to module's __init__ ?
FRAMEWORK_VERSION = '1.0'
# aliases
M = Measurement
STOP = htf.PhaseResult.STOP
CONTINUE = htf.PhaseResult.CONTINUE
REPEAT = htf.PhaseResult.STOP
options = htf.PhaseOptions

REQUIRED_ATTRS = ['VERSION', 'TESTS']

# allows @Test.test decorator
def test(f):
    @htf.TestPhase()
    def deco(*args, **kw):
        f(*args, **kw)
    return deco

### JSON output stuff
# move to output lib file
OUTPUT_DIR = './results/'
OUTPUT_FMT_STRING = '{metadata[type]}.{dut_id}.{metadata[test_name]}-v{metadata[test_version]}.json'
OUTPUT_JSONFILE = '{}{}'.format(OUTPUT_DIR, OUTPUT_FMT_STRING)

### fake DB stuff
DEVICES = []
META = {}

### dev symbols
DEBUG = False
# XXX: hack for not having a real mainboard to iceboot for dev
FAKE_ICEBOOT = False
  
    #test = lambda: htf.TestPhase

# XXX: this is gotten from the "database" ;)
# XXX: part of test db layer (lib/db.py ?)
class ParamDB:
    @staticmethod
    def getTestParam(test_name, param_list):
        DB_PARAMS = {
            'fw_vnum_test': {
                'expected_fw_vnum': '0x6a'
            },
            'foo': {
                'min': 40,
                'max': 44
            }
        }
        ret = {}
        for p in param_list:
            ret[p] = DB_PARAMS[test_name][p]
        return ret


### MAIN CODE

class Test():
    def __init__(self, version, params={}, config={}):
        self.tests = []
        self.config = config
        self.test_params = params
        self.version = None


    def addTest(self, testCallable):
        self.tests.append(testCallable)

    def getTestParams(self, func):
        if not getattr(self, 'test_params') or not self.test_params:
            return {} 
        pname = func.__name__
        if pname not in self.test_params:
            return {}

        # lookup param values
        plist = self.test_params[pname]
        return ParamDB.getTestParam(pname, plist)

    def execute(self, device):
        # test disco?
        try:
            self.tests = self.TESTS
        except AttributeError:
            # not a Runnable test
            return

        #self.
        #self.test.logger.info('executing test')
        #device = self.config.get('device', {})
        cls = str(self.__class__).split('.')[1]
        #test_name = '{}-v{}'.format(cls, self.version)
        test_name = cls

        desc = getattr(self, 'DESC', self.__doc__)

        phases = []
        for x in self.tests:
            # check for params
            try:
                if hasattr(x, '_checkpoint'):
                    raise AttributeError
                args = self.getTestParams(x.func)
                phases.append(x.with_args(session=self.session, **args))
            except AttributeError:
                phases.append(x)

#.with_args(T, T.meta, T.measurements, {}),

        T = htf.Test(
            *phases,
            # openhtf fields
            test_name=test_name,
            test_version=self.version,
            test_desc=desc or 'no description',
            # custom metadata fields
            framework_version=FRAMEWORK_VERSION,
            device=device,
            type=device['type'],
            testOptions=self.config.get('device', {})
        )

        T.add_output_callbacks(JSON(OUTPUT_JSONFILE, indent=4, default=str))

        # get session here???
        #T.session = getIcebootSession(fake=FAKE_ICEBOOT,
        #    self.CONFIG.get)
        T.execute(test_start=lambda: device['id'])
        

def getIcebootSession(fake=False, **kw):
    if not fake:
        # TODO: fix iceboot config opts
        # XXX: can't use optparse with argparse :(
        class IcebootOpts:
            host = '192.168.0.10'
            port = 5012
            debug = False
            fpgaConfigurationFile = 'fw_0x6a.rbf'
            test = []

        print '(framework) Starting iceboot session ...'
        if kw:
            print '(framework) using overrides: {}'.format(json.dumps(kw))
        return iceboot_session_cmd.init(IcebootOpts, **kw)

    class Iceboot:
        def __init__(self, **kw):
            self.status = 'OK' if not 'status' in kw else 'Error'
            self.wait = 0

        def __repr__(self):
            return 'iceboot'
        __str__ = __repr__

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
    global DEVICES
    global META 
    # pretend to be a db interface...
    if not DEVICES:
        with open('db/all.json', 'r') as f:
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



class MainboardTest(Test):
    def __init__(self, version, **kw):
        Test.__init__(self, version, **kw)
        self.config['test'] = {}
        self.config['device'] = {}
        self.session = getIcebootSession(fake=FAKE_ICEBOOT,
            **self.config.get('iceboot', {})
        )
       # getattr(self, 'FAKE_ICEBOOT', False))
        self.version = self.VERSION


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

        

def run(testClass=None):
    '''
    This function magically runs either one test or all in a file 
    '''
    # XXX: for dev purposes, fake iceboot on my system only
    global FAKE_ICEBOOT
    import os
    FAKE_ICEBOOT = os.environ.get('FAKE_ICEBOOT', False)


    mainboard = getDevices('mainboard')
    device = mainboard[0]

    if testClass:
        testClasses = [testClass]
    else:
        # get class methods
        import inspect
        frame = inspect.stack()[1]
        mod = inspect.getmodule(frame[0])


        # XXX: for now... only allow classes with "Test" in the name
        testClasses = [getattr(mod, x) for x in dir(mod) if 'Test' in x and x != 'Test']

    ran = False
    for testClass in testClasses:
        if _run(testClass, device):
            ran = True

    if not ran:
        print 'No tests found :('
    # instantiate class(es)

    # run execute() method

def _run(testClass, device):
      # XXX: for now, we use TESTS to determine whether to run
      # if hasattr(testClass, 'TESTS'):
      # see if this is a runnable test
      if not check_attrs(testClass, required=False):
          if DEBUG:
              print 'Skipping {}'.format(testClass.__name__)
          return False

      test = testClass(
        testClass.VERSION,
        params=getattr(testClass, 'PARAMS', {}),
        config=getattr(testClass, 'CONFIG', {})
      )
      test.execute(device)
      return True


### VALIDATORS

@htf.util.validators.register
def equalsParam(pname, type=None):
    if not (pname.startswith('{') and pname.endswith('}')):
        pname = '{' + pname + '}'
    return EqualsParam(pname, type=type)

class EqualsParam(htf.util.validators.ValidatorBase) :
    def __init__(self, pvalue, type=None):
        self.paramValue = pvalue
        self._type = type
        

    def with_args(self, **kw):
        return type(self)(
            pvalue=htf.util.format_string(self.paramValue, kw),
            type=kw.get('type', None),
        )

    def __call__(self, value):
        return self.paramValue == value
