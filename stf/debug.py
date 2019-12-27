import os
from .util.colors import termcolor as clr
from . import PYTHON3
from . import _PRINT as prnt
from .util.misc import setInfoGroups

### dev symbols
class DEBUG:
    LOG = os.environ.get('STF_DEBUG', False)
    # create "fake" iceboot 
    FAKE_ICEBOOT = os.environ.get('STF_FAKEICEBOOT', False)
    # skip loading of FW file
    SKIP_FW = os.environ.get('STF_SKIPFW', False)
    # allow print statements in test files
    ALLOW_PRINT = True
    p = os.environ.get('STF_ALLOWPRINT', True)
    if p in ['false', 'False', '0', 0]:
        ALLOW_PRINT = False

    # don't call json_minify on json (use this in case of problems)
    NOSTRIPJSON = os.environ.get('STF_NOSTRIPJSON', False)

def dbg(s, trace=5):
    if DEBUG.LOG:
        if not isinstance(s, str):
            s = str(s)
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
        prnt('{} {} {}'.format(
            clr('DEBUG >>', 'red'),
            clr(trace, 'gray'),
            clr(s, 'aqua')
        ))
debug = dbg
