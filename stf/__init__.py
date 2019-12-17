from __future__ import print_function

__version__ = '0.2'
FRAMEWORK_VERSION = __version__


global TESTABLE_CLASSES
TESTABLE_CLASSES = []

def addTestClass(cls):
    global TESTABLE_CLASSES
    TESTABLE_CLASSES.append(cls)

def getRegisteredClasses():
    return TESTABLE_CLASSES

import sys
import os

# directories:
STF_HOME = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(STF_HOME, 'tools', 'python'))

try:
    import builtins as __builtins__
except ImportError:
    pass

# save ref to original print fn
try:
    _PRINT = __builtins__.print
except AttributeError:
    _PRINT = __builtins__['print']
    PYTHON2 = True
    PYTHON3 = False
else:
    PYTHON3 = True
    PYTHON2 = False

# hack to redirect print statements to test logger.info
'''
#XXX: print_smasher?
def print_smash(*args):
    pass
__builtins__.print = print_smash
'''

from .debug import dbg, DEBUG

if PYTHON3:
    def printToInfo(*args):
        try:
            # get test object
            #... hmm, maybe something like?
            test = sys._getframe(1).f_locals["test"]
            s = 'print: ' + ' '.join([str(a) for a in args])
            test.logger.info(s)
        except:
            #from .debug import dbg
            # _PRINT(*args) here? or ignore?
            if DEBUG.ALLOW_PRINT:
                _PRINT(*args)
            else:
                dbg('Error! BAD PRINT {}'.format(args))
    __builtins__.print = printToInfo

# XXX: todo -- create JSON based config file for STF itself
class ENV():
    def __dir(*args):
        return os.path.join(STF_HOME, '..', *args)

    DATA_DIR = __dir('data')
    TEST_DIR = __dir('tests')
    TEST_CONFIG_DIR = __dir(DATA_DIR, 'testconfig')
    DB_DIR = DATA_DIR

    __DIR = __dir('results')
    __FMT_STRING = '{metadata[test_name]}-v{metadata[test_version]}-degg-{dut_id}.json'
    JSONFILE_NAME = __dir(__DIR, __FMT_STRING)

    FIRMWARE_VERSION = 0xb0
    FIRMWARE_FILE_PATH = __dir(DATA_DIR, 'fw_{}.rbf'.format(hex(FIRMWARE_VERSION)))

    # this is a db placeholder hackjob (i.e. this will be removed someday)
    DEVICES_JSON_FILE = os.path.join(DB_DIR, 'all.json')

#from I3Test import *
debug = dbg
from .core import run

# core aliases
Measurement = M = core.htf.Measurement

FAIL_AND_DIE = core.htf.PhaseResult.STOP
STOP = core.htf.PhaseResult.STOP

CONTINUE = core.htf.PhaseResult.CONTINUE
PASS = core.htf.PhaseResult.CONTINUE

FAIL = core.htf.PhaseResult.FAIL_AND_CONTINUE

REPEAT = core.htf.PhaseResult.REPEAT
options = core.htf.PhaseOptions
measures = core.htf.measures

# just an option to explicitly state you won't be loading a config
# (this should probably be discouraged)
NOCONFIG = '__skip_stf_config__'

from .decorators import register
# for stf.test decorator
from .decorators import make_test as test
#register, equalsParam
#from .decorators import *
from . import testclasses


