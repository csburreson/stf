import json
import time
import openhtf as htf
# XXX: this monkey-patch fixes JSON serialization problems with numpy arrays in
# test.measurements
x = htf.data.convert_to_base_types
def foo(*a, **k):
  try:
    return a[0].tolist()
  except AttributeError:
    return x(*a, **k)
htf.data.convert_to_base_types = foo
# XXX end hack
import threading
from openhtf import measures, Measurement
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.util.checkpoints import checkpoint as CHECKPOINT

# first is for local dev setup 
from .tools.python.iceboot import iceboot_session_cmd
from . import db

from stf.debug import dbg, DEBUG
from stf import getRegisteredClasses, getRegisteredClassesByName, getClassContext, getRegisteredClass, _PRINT, delClassContext, INFO, ginfo 
from .parse import SetConfig
from .util import files 
from .util.colors import termcolor as tc
from .util.config import get_config

CONFIG = get_config()


### fake DB stuff
DEVICES = []
META = {}


class FakeIceboot(object):
    '''
    placeholder class for development which accepts any method call
    and returns nothing
    '''
    def __init__(self, *args, **kw):
        dbg('Creating FAKE iceboot class with (unused) kwargs: {}'.format(kw))
        self.FAKE = True

    def __getattr__(self, attr):
        def fake(*args, **kw):
            f = kw.get('retval', '')
            if f is not None:
                if callable(f):
                    return f()
                return f
            return None
        if attr == 'fpgaVersion':
            return lambda: int(CONFIG.settings.iceboot.fw_version, 16)
        return fake

def getIcebootSession(**kw):
    if DEBUG.FAKE_ICEBOOT:
        return FakeIceboot(**kw)

    class IcebootOpts:
        host = CONFIG.settings.iceboot.host
        port = CONFIG.settings.iceboot.port
        debug = CONFIG.settings.iceboot.debug
        fpgaConfigurationFile = None

    dbg('Starting iceboot session ...')
    dbg(f'  {CONFIG.settings.iceboot}')
    session = None
    fail_count = 0
    # XXX:
    #kw = CONFIG.getIcebootOpts()
    while session is None and fail_count < 5:
        try:
            # this sleep prevents OSError from being thrown in some
            # circumstances
            session = iceboot_session_cmd.init(IcebootOpts, **kw)
            time.sleep(3)

        except (IOError, OSError):
            # this except doesn't seem to trigger anymore with the sleep, but
            # just in case...
            fail_count += 1
            dbg("OSERROR!!!")
            session = None
            if fail_count == 5:
                raise

    return session


def getDevices(device_type=None):
    '''
    pretend to be a db interface...
    '''
    global DEVICES
    global META 
    if not DEVICES:
        fname = CONFIG.get_path('data', CONFIG.settings.device.source)
        with open(fname, 'r') as f:
            DB = json.load(f)
        DEVICES = DB['devices']
        META = DB['meta']

    if device_type:
        return [d for d in DEVICES if d["type"] == device_type]
    return DEVICES
        

# test running code 

def run(dhost=CONFIG.settings.iceboot.host, 
        dport=CONFIG.settings.iceboot.port,
        dtype='degg'):
    '''
    run should discover devices (TODO) and loop over and run all registered
    tests
    '''
    #mainboard = getDevices('mainboard')
    #device = mainboard[0]
    dut_id = getBoardID(host=dhost, port=dport)
    device = {
        'id': dut_id,
        'type': dtype
    }
    # must ensure output directory exists for this device
    device_dir = '{type}-{id}'.format(**device)
    files.mkdir(
        CONFIG.get_path('results'),
        device_dir
    )

    ran = False
    for testClass in getRegisteredClasses():
        dbg("Running {}".format(testClass.test_name))
        testClass.execute(device, {'iceboot': dict(host=dhost, port=dport)})
        ran = True

    if not ran:
        dbg('Nothing ran :(')
        pass

def _run(testClass, device):
      return True

def run_set(set_name=None, config_file=None, list_tests=False, list_overrides=False, device_type='degg',
            device_host=CONFIG.settings.iceboot.host, device_port=CONFIG.settings.iceboot.port):
    if set_name:
       config_file = CONFIG.get_path('setconfig', filename=f'{set_name}.json')
       if not files.exists(config_file):
           raise Exception('Cannot find {}'.format(config_file))

    if not config_file:
       raise Exception('Must provide config file or set name')

    if not set_name:
        set_name = files.getNameFromPath(config_file)

    setConfig = SetConfig(config_file, set_name)
    '''
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tests.Interlock import run_test
    from tests import Interlock
    from tests import ADCNoiseLevel
    dbg(dir(Interlock))
    Interlock.STF_RUN_TEST()
    '''

    #conns = [('10.134.32.51', device_port), ('localhost', '5012')]
    conns = [(device_host, device_port)]
    threads = []

    STF_USE_THREADS = False

    for host, port in conns:
        ### VERIFY CONFIG
        for test in setConfig.tests:
            d = CONFIG.get_path('tests')
            testFile = f'{d}/{test}.py'
            dbg('verifying testfile {} ...'.format(testFile))
            try:
                with open(testFile) as f:
                    testCode = f.read()
                exec(compile(testCode, testFile, 'exec'))
            except:
                dbg('exception when running {}'.format(testFile))
                raise
            #from .. import tests as definedTests
            #dbg(dir(definedTests[test]))

        setConfig.configure()
        
        #dbg('registered_tests: {}'.format(getRegisteredClassesByName().keys())) 
        dbg(setConfig.instances)

        # maybe the results path should include results/setname/{dut_id}-{timeSlug} wehre timeSlug has minutes precision (or we just add sequence numbers...
        # maybe dut_id-suquence-timeslug? since the 
        # XXX: just thought of this; should timeSlug be property of class at time of instantion? or passed from runset code? because it should be the same for all test outputs...
        '''
        files.ensureEmptyDir(
            root=CONFIG.get_path('results'),
            dirs=[setConfig.set_name,
            setConfig.time_slug],
            # delete in case of duplication?
            delete_pattern='*.json'
        )
        '''
        if STF_USE_THREADS:
            t = threading.Thread(target=runset_thread, args=(setConfig, host, port, device_type))
            t.start()
            dbg(f'Creating thread... runset_thread -> runset="{setConfig.set_name}" args=( "{host}", "{port}", "{device_type}")')
            threads.append(t)
        else:
            runset_thread(setConfig, host, port, device_type)

    if STF_USE_THREADS:
        dbg('Threads created... joining')
        for t in threads:
            t.join()
            #runset_thread(setConfig, device_host, device_port, device_type)


def runset_thread(setConfig, device_host, device_port, device_type, list_tests=False, list_overrides=False):
    def debug(s):
        dbg('XXX: {}:{}:{} {}'.format(setConfig.set_name, device_host, device_port, s))
    debug('Creating results dir for {setConfig.set_name}/{setConfig.time_slug}')

    # check for board ID
    dut_id = getBoardID(host=device_host, port=device_port)

    # NOTE: must match config.output.json.filename
    device_dir = '{}-{}'.format(device_type, dut_id)
    files.mkdir(
        CONFIG.get_path('results'),
        setConfig.set_name,
        setConfig.time_slug,
        device_dir
    )

    for test in setConfig.instances:
        testName = test['test_name']
        debug('running: {}'.format(test['testinstance_name']))
        debug('   with: {}'.format(test))

        # XXX: refactor test/config listing to be insdie of setConfig
        # then modify runset script to just ask setConfig for this stuff
        if list_tests:
            _PRINT(test['testinstance_name'])
            continue
        if list_overrides:
            _PRINT(test['testinstance_name'])
            _PRINT(f"  args: {test['args']}")
            _PRINT(f"  expv: {test['expectedValues']}")
            _PRINT('')
            continue

        testFile = CONFIG.get_path('tests', filename=f'{testName}.py')

        with open(testFile) as f:
            testCode = f.read()
            code = f"""\nstf.core.run_single_test("{testName}", "{test['instance_name']}", "{setConfig.set_name}", {test['args']}, {test['expectedValues']}, "{setConfig.time_slug}", "{dut_id}", "{device_type}", "{device_host}", "{device_port}")"""
            debug(f'code: {code}')
            cc = getClassContext(testName)
            exec(compile(testCode + code, testFile, 'exec'), cc[2])


def run_single_test(name, instance, group, args, evs, timeslug, 
                    dut_id, dut_type='degg', dut_host=None, dut_port=None):
    test = getRegisteredClass(name)
    cName = tc(name, 'aqua')
    cInst = tc(instance, 'aqua')

    INFO(f'Running {cName}:{cInst}', groups=['runset', 'framework'])

    # XXX: copy class info? clone method? maybe just 
    # return new Test object with test.reconfigure()?
    #test.reconfigure(instance, group, args, evs, timeslug, {})
    #T = test.deriveInstance(instance, group, args, evs, timeslug=timeslug, config={})

    # XXX: multiple devices
    try:
        test.execute( {
            'id': dut_id, 
            'type': dut_type
        }, {
            'iceboot': {
                'host': dut_host,
                'port': dut_port,
                'debug': CONFIG.settings.iceboot.debug
            },
            'instance': {
                'args': args,
                'expectedValues': evs,
                'instance': instance,
                'group': group,
                'group_timeslug': timeslug
            }
        })
    except KeyboardInterrupt:
        raise
    except:
        INFO(f'Exception raised during test {name}:{instance}')


def getBoardID(host=None, port=None):
    session = getIcebootSession(host=host, port=port)
    x = session.flashID()
    del session
    return x
