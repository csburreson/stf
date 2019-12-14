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

    FIRMWARE_FILE_PATH = __dir(DATA_DIR, 'fw_0x6a.rbf')

    # this is a db placeholder hackjob (i.e. this will be removed someday)
    DEVICES_JSON_FILE = os.path.join(DB_DIR, 'all.json')

#from I3Test import *
from .debug import dbg, DEBUG
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

from .decorators import register
# for stf.test decorator
from .decorators import make_test as test
#register, equalsParam
#from .decorators import *
from . import testclasses


