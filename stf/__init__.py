from __future__ import print_function
from collections import OrderedDict

__version__ = '1.3a'
FRAMEWORK_VERSION = __version__
FRAMEWORK_VERSIONNAME = 'Chernobyl'

# exception class for folks to throw known exceptions
# NOTE: move to util/exceptions.py and include other STF-based exceptions that
# are common across tests (if there are any)
class STFException(Exception):
    pass


global TESTABLE_CLASSES
TESTABLE_CLASSES = OrderedDict() 
global CLASS_CONTEXT 
CLASS_CONTEXT = {}

def addTestClass(name, cls, test_locals, test_globals, code_obj=None):
    global TESTABLE_CLASSES
    TESTABLE_CLASSES[name] = cls
    CLASS_CONTEXT[name] = (code_obj, test_globals, test_locals)


def getClassContext(name):
    return CLASS_CONTEXT[name]

def delClassContext(name):
    del CLASS_CONTEXT[name]
#def delTestClass

def getRegisteredClasses():
    return TESTABLE_CLASSES.values()

def getRegisteredClassesByName():
    return TESTABLE_CLASSES

def getRegisteredClass(name):
    return TESTABLE_CLASSES[name]

import sys
import os

# directories:
#STF_HOME = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(STF_HOME, 'tools', 'python'))
# directories:
__TMP = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(__TMP, 'tools', 'python'))
STF_HOME = os.path.realpath(os.path.join(__TMP, '..'))


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


from .debug import dbg, DEBUG

from stf.util.misc import INFO, get_InfoWithGroups as ginfo


if PYTHON3:
    def printToInfo(*args, **ignored):
        try:
            # get test object
            test = sys._getframe(1).f_locals["test"]
            s = 'print: ' + ' '.join([str(a) for a in args])
            test.logger.info(s)
        except:
            # _PRINT(*args) here? or ignore?
            if DEBUG.ALLOW_PRINT:
                _PRINT(*args)
            else:
                dbg('Error! BAD PRINT {}'.format(args))
    __builtins__.print = printToInfo


debug = dbg
from .util.config import get_config
config = get_config(f'{STF_HOME}/stfconfig.json', f'{STF_HOME}/stfconfig.local.json')
from .core import run, run_set
from . import parse
from . import util

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


