__version__ = '0.2'

#from I3Test import *
from core import *
from decorators import register
import testclasses

global TESTABLE_CLASSES
TESTABLE_CLASSES = []

import os
# directories:
STF_HOME = os.path.dirname(os.path.realpath(__file__))

class env():
    def __dir(*args):
        return os.path.join(STF_HOME, *args)

    DATA_DIR = __dir('data')
    TEST_DIR = __dir(DATA_DIR, 'testconfig')
    DB_DIR = DATA_DIR



