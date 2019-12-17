import json
import openhtf as htf
#from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.output.callbacks import console_summary
from .core import getIcebootSession
from .output import OutputToJSON as JSON
import stf
FAKE_ICEBOOT = False

#JSON.json_encoder = STFJSONEncoder

class TestSet(object):
    def __init(self, version):
        pass

@htf.util.validators.register
def equalsParam(pname, type=None):
    if not (pname.startswith('{') and pname.endswith('}')):
        pname = '{' + pname + '}'
    return EqualsParam(pname, type=type)


class EqualsParam(htf.util.validators.ValidatorBase):
    def __init__(self, pvalue, type=None):
        self.paramValue = pvalue
        self._type = type

    def __call__(self, value):
        return self.paramValue == value
        
    def __str__(self):
        '''use in output'''
        return 'x == {}'.format(self.paramValue)

    def with_args(self, **kw):
        try:
            return type(self)(
                pvalue=htf.util.format_string(self.paramValue, kw['expectedValues']),
                type=kw.get('type', None),
            )
        except KeyError:
            raise Exception('Framework Error. Contact maintainer')

class Common(object):
    # default test config options
    TEST_CONFIG = {
        'timeout_s': 10
    }
    @stf.measures(stf.M('fw_vnum'))
    # XXX: fix this later (use a different validator) 
    # # .equalsParam('expected_fw_vnum'))
    def checkCommsAndFirmware(test, session, **kw):
        vn = session.fpgaVersion()
        stf.dbg('running framework FW test, got vn: {} (expecting {})'.format(hex(vn), kw['expectedValues']['expected_fw_vnum']))
        test.measurements.fw_vnum = hex(vn)
        if vn == 0xFFFF:
            test.logger.error('no firmware detected. quitting.')
            return stf.STOP


    def setupIceboot(test, session):
        self.session = getIcebootSession(fake=FAKE_ICEBOOT,
            **self.config.get('iceboot', {})
        )

class MainboardTest(object):
    def __init__(self, version, test_name, test_fn=None, **kw):
        stf.dbg('creating MainboardTest class for: {}'.format(test_name))
        self.tests = []

        # optional description
        self.desc = kw.get('test_desc') or 'n/a; see test file: {}'.format(test_name)

        # test_params is a map of fn name = list of varnames
        self.test_params = kw.get('params', {})
        self.test_name = test_name
        if not callable(test_fn):
            raise Exception('Invalid "test_fn" parameter. Expecting callable')
        self.test_fn = test_fn
        self.version = version
        # instance can be none
        self.instance = kw.get('instance')

        self.session = None
        # XXX: move to init or "configure" step or something
        self.config = Common.TEST_CONFIG
        conf_file = kw['conf_file']

        # skip loading config
        if conf_file == stf.NOCONFIG:
            self._PARAMS = {'args': {}, 'expectedValues': {}}
            self._PARAM_CONF_FILE = None
            return

        with open(conf_file, 'r') as f:
            stf.dbg("(@configure) loaded {}".format(conf_file))
            try:
                self._PARAMS = json.load(f)
            except json.decoder.JSONDecodeError:
                raise Exception('Invalid test configuration file! Is this valid JSON?')
            self._PARAM_CONF_FILE = conf_file
            stf.dbg("(@configure) {}".format(self._PARAMS))
            if 'config' in self._PARAMS:
                cfg = self._PARAMS['config']
                stf.dbg('@configure: config overrides: {}'.format(cfg))
                self.config.update(cfg)
                stf.dbg('@configure: full config: {}'.format(self.config))

            #if 'expectedValues' in self._PARAMS:



        # XXX:
        # create iceboot session here?
        # or as a test phase?
    def setupIceboot(self, test):
        self.session = getIcebootSession(fake=FAKE_ICEBOOT,
            **self.config.get('iceboot', {
                'host': 'localhost',
                'port': 5012
            })
        )

    def setup(self, test):
        # placeholder for OpenHTF setup phase
        pass

    def tearDown(self, test):
        # placeholder for OpenHTF tearDown phase
        pass

    # DEPRECATED
    def addTest(self, testCallable):
        self.tests.append(testCallable)

    def getTestParams(self):
        '''
        pname = "test name" but should probably be thought of as "phase name"

        self._PARAMS is dict of {
            "test (phase) name": {
                "varname": "value"
            }
        }
        '''
        # XXX: this requires @configure deco
        if hasattr(self, '_PARAMS'):
            return self._PARAMS

        # deprecated (bwloe)
        if not getattr(self, 'test_params') or not self.test_params:
            return {} 

        #pname = func
        if pname not in self.test_params:
            return {}

        # lookup param values
        plist = self.test_params[pname]
        get_db()
        return ParamDB.getTestParams(pname, plist)
    
    def get_session(self):
        return self.session

    def execute(self, device):
        # could we get params from the fn itself and possibly declare them with
        # defaults with a decorator, eliminating the need for a testconfig
        # file? if so, would it buy us much? probably not
        ps = self.getTestParams()

        # could get device config here:
        # dev_conf = getDeviceConfig(device)

        # TODO: get test desc (or keep this in DB and link to test name)
        desc = 'todo'

        # get test arguments (from json file)
        test_args = ps.get('args', {})
        stf.dbg('test args: {}'.format(test_args))
        expected_values = ps.get('expectedValues', {})
        stf.dbg('expected values: {}'.format(expected_values))

        # get test configuration options (defaults hardcoded, override in test config file
        # with "conf" top-level key
        #defaults = testclasses.Common.TEST_CONFIG

        # by default fpgaConfigurationFile is set in getIcebootSession
        # if a key is provided and the value is None/null, it will be
        # skipped
        iceboot_conf = self.config.get('iceboot', {})

        # XXX: move this to seutp function or re-implement this as a plug?
        self.session = getIcebootSession(fake=stf.DEBUG.FAKE_ICEBOOT, **iceboot_conf)

        if expected_values:
            test_args['expectedValues'] = expected_values

        phases = [
            Common.checkCommsAndFirmware.with_args(session=self.session, expectedValues={'expected_fw_vnum':stf.ENV.FIRMWARE_VERSION}),
            self.test_fn.with_args(session=self.session, **test_args)
            #run_test.with_plugs(session=IcebootSession).with_args(**test_args)
        ]

        T = htf.Test(htf.PhaseGroup(
                #setup=[self.setupIceboot],
                setup=[self.setup],
                main=phases,
                teardown=[self.tearDown]
            ),
            # openhtf fields
            test_name=self.test_name,
            test_version=self.version,
            test_desc=self.desc,
            # custom metadata fields
            framework_version=stf.FRAMEWORK_VERSION,
            device=device,
            testOptions={
                'params': test_args
            }
        )

        def try_list(x):
            try:
                return x.tolist()
            except AttributeError:
                return str(x)

        # XXX: how to deal with output options?
        T.add_output_callbacks(
            JSON(stf.ENV.JSONFILE_NAME, indent=4, default=try_list)
        )

        # XXX: add DEBUG flag?
        T.add_output_callbacks(
            console_summary.ConsoleSummary()
        )

        T.execute(test_start=lambda: device['id'])

        stf.dbg("finished execute for test: {}".format(self.test_name))



    def executeOLD(self, device):
        # test disco?
        try:
            self.tests = self.TESTS
        except AttributeError:
            print( "Error! No TESTS property found")
            # not a Runnable test
            return

        #self.test.logger.info('executing test')
        #device = self.config.get('device', {})
        cls = str(self.__class__).split('.')[1]
        #test_name = '{}-v{}'.format(cls, self.version)
        test_name = cls

        desc = getattr(self, 'DESC', self.__doc__)

        phases = []
        test_args = {}
        for x in self.tests:
            # check for params
            try:
                #qualified_testname = '{}.{}'.format(
                #    self.__class__.__name__, 
                #    x.func.__name__
                #)
                #args = self.getTestParams(qualified_testname)
                fn_name = x.func.__name__
                if fn_name == '_checkpoint':
                    stf.dbg('CHECKPOINT')
                    phases.append(x)
                    continue
                args = self.getTestParams()
                test_args[fn_name] = args

                stf.dbg(fn_name)
                #dbg('{}.{}'.format(self.__class__.name, fn_name))
                stf.dbg('optname: {}'.format(x.options.name))
                phases.append(x.with_args(session=self.session, **args))
            except AttributeError:
                # XXX
                stf.dbg('AttrErr')
                #x = test(x)
                phases.append(x)


        #phases = [test_fn]
        T = htf.Test(
            *phases,
            # openhtf fields
            test_name=self.test_name,
            test_version=self.version,
            test_desc=desc or 'no description',
            # custom metadata fields
            framework_version=FRAMEWORK_VERSION,
            device=device,
            type=device['type'],
            testOptions={
                'params': test_args
            }
            #self.config.get('device', {})
        )

        T.add_output_callbacks(
            JSON(OUTPUT_JSONFILE, indent=4, default=str)
        )

        # get session here???
        #T.session = getIcebootSession(fake=FAKE_ICEBOOT,
        #    self.CONFIG.get)
        T.execute(test_start=lambda: device['id'])
        

'''
class MainboardTestOLD(Test):
    def __init__(self, version, **kw):
        Test.__init__(self, version, **kw)
        self.config['test'] = {}
        self.config['device'] = {}
        self.session = getIcebootSession(fake=FAKE_ICEBOOT,
            **self.config.get('iceboot', {})
        )
        self.version = self.VERSION
'''
