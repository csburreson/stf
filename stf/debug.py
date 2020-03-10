import os
from .util.colors import termcolor as clr

### dev symbols
class DEBUG:
    LOG = os.environ.get('STF_DEBUG', False)
    # create "fake" iceboot 
    FAKE_ICEBOOT = os.environ.get('STF_FAKEICEBOOT', False)
    # skip loading of FW file
    SKIP_FW = os.environ.get('STF_SKIPFW', False)

def dbg(s, trace=5):
    if DEBUG.LOG:
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
