'''
This is the core file for the testing api

the test designers should not need to read this

TODO: create module and make this "core" with "Test.Test" (mod.class) an alias for <mod>/core.py:Test
'''

import openhtf as htf
from openhtf import measures, Measurement
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.util.checkpoints import checkpoint as CHECKPOINT
import json

FRAMEWORK_VERSION = '1.0'

M = Measurement
STOP = htf.PhaseResult.STOP
CONTINUE = htf.PhaseResult.CONTINUE

REQUIRED_ATTRS = ['VERSION', 'TESTS']

# decorator
#def test(f):
    #def wrap(self):
DEVICES = []
META = {}

DEBUG = False

# allows @Test.test decorator
def test(f):
    @htf.TestPhase()
    def deco(*args, **kw):
        f(*args, **kw)
    return deco
  
    #test = lambda: htf.TestPhase

class Test():

    def __init__(self, version):
        self.tests = []
        self.config = {}
        self.version = None


    def addTest(self, testCallable):
        self.tests.append(testCallable)

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
            try:
                if hasattr(x, '_checkpoint'):
                    raise AttributeError
                phases.append(x.with_args(session=self.session))
            except AttributeError:
                phases.append(x)


        T = htf.Test(
            #*[x.with_args(session=self.session) for x in self.tests],
            *phases,
            # openhtf fields
            test_name=test_name,
#.with_args(T, T.meta, T.measurements, {}),
            test_version=self.version,
            test_desc=desc or 'no description',
            framework_version=FRAMEWORK_VERSION,
            device=device,
            type=device['type'],
            testOptions=self.config.get('device', {})
        )
        T.add_output_callbacks(JSON('./results/{metadata[type]}.{dut_id}.{metadata[test_name]}-v{metadata[test_version]}.json', indent=4, default=str))

        T.execute(test_start=lambda: device['id'])
        

#def measures(*args):
#    return htf.measures(*args)


def getIcebootSession():
    class Iceboot:
        def __init__(self, **kw):
            self.status = 'OK' if not 'status' in kw else 'Error'

        def __repr__(self):
            return 'iceboot'
        __str__ = __repr__

        def cmd(self, x):
            if x == 'funkItUp':
                self.status='Error'
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
    def __init__(self, version):
        Test.__init__(self, version)
        self.config['test'] = {}
        self.config['device'] = {}
        self.session = getIcebootSession()
        self.version = self.VERSION


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
          if hasattr(testClass, 'TESTS') == True:
              print ">> No VERSION found for {}\n\n".format(testClass.__name__)
          if DEBUG:
              print 'Skipping {}'.format(testClass.__name__)
          return False
      test = testClass(testClass.VERSION)
      test.execute(device)
      return True

