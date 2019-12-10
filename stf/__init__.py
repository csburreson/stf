__version__ = '0.2'

#from I3Test import *
from .core import *
from .decorators import *
#register, equalsParam
#from .decorators import *
from . import testclasses

global TESTABLE_CLASSES
TESTABLE_CLASSES = []

def addTestClass(cls):
    global TESTABLE_CLASSES
    TESTABLE_CLASSES.append(cls)

import os
# directories:
STF_HOME = os.path.dirname(os.path.realpath(__file__))

class env():
    def __dir(*args):
        return os.path.join(STF_HOME, '..', *args)

    DATA_DIR = __dir('data')
    TEST_DIR = __dir('tests')
    TEST_CONFIG_DIR = __dir(DATA_DIR, 'testconfig')
    DB_DIR = DATA_DIR

    __DIR = __dir('results')
    __FMT_STRING = '{metadata[test_name]}-v{metadata[test_version]}-degg-{dut_id}.json'
    JSONFILE_NAME = __dir(__DIR, __FMT_STRING)

ENV = env
