import json
import time
import openhtf as htf
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.output.callbacks import console_summary
from .core import getIcebootSession
from .validators import *
import stf
from .util.colors import termcolor as clr
from .util.misc import INFO
FAKE_ICEBOOT = False

class TestSet(object):
    def __init(self, version):
        pass




class Common(object):
    # default test config options
    TEST_CONFIG = {
        'timeout_s': 10
    }
    @stf.measures(stf.M('fw_vnum').equals(hex(stf.ENV.FIRMWARE_VERSION)))
    #XXX: need long timeout for localhost from crappy inet cnxn
    @stf.options(timeout_s=500)
    def checkCommsAndFirmware(test, session, **kw):
        vn = session.fpgaVersion()
        stf.dbg('running framework FW test, got vn: {} (expecting {})'.format(hex(vn), kw['expectedValues']['expected_fw_vnum']))

        gINFO = stf.ginfo(['framework', 'iceboot'])
        if not session.flashLS():
            gINFO(f'uploading fw file to flash ({stf.ENV.FIRMWARE_FILE_PATH})... \n\t(this could take a while)')
            #session.ymodemConfigureCycloneFPGA(stf.ENV.FIRMWARE_FILE_PATH)
            session.ymodemFlashUpload(stf.ENV.FIRMWARE_FILE_REMOTE, stf.ENV.FIRMWARE_FILE_PATH)
        gINFO(f'configuring fw file from flash ({stf.ENV.FIRMWARE_FILE_REMOTE})...')
        session.flashConfigureCycloneFPGA(stf.ENV.FIRMWARE_FILE_REMOTE)

        vn = session.fpgaVersion()
        test.measurements.fw_vnum = hex(vn)
        if vn == 0xFFFF:
            test.logger.error('no firmware detected. quitting.')
            return stf.STOP



    '''
    def setupIceboot(test, session):
        if session:
            INFO("HERE")
            del self.session
            import time
            time.sleep(5)
        #self.session = getIcebootSession(**stf.config.getIcebootOpts())
        '''

class MainboardTest(object):
    def __init__(self, version, test_name, test_fn=None, **kw):
        stf.dbg('creating MainboardTest class for: {}'.format(test_name))
        self.tests = []
        self.group = kw.get('group')

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

        #self.session = None
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
                self._PARAMS = stf.parse.json_load(f)
            except json.decoder.JSONDecodeError:
                raise Exception('Invalid test configuration file! Is this valid JSON?')
            self._PARAM_CONF_FILE = conf_file
            stf.dbg("(@configure) {}".format(self._PARAMS))
            if 'config' in self._PARAMS:
                cfg = self._PARAMS['config']
                stf.dbg('@configure: config overrides: {}'.format(cfg))
                self.config.update(cfg)
                stf.dbg('@configure: full config: {}'.format(self.config))

        if not 'args' in self._PARAMS:
            self._PARAMS['args'] = {}
        if not 'expectedValues' in self._PARAMS:
            self._PARAMS['expectedValues'] = {}

        # XXX:
        # create iceboot session here?
        # or as a test phase?
    def setupIceboot(self, test):
        #if session:
        #    INFO("HERE")
        #    del self.session
        #    import time
        #    time.sleep(5)
        self.session = getIcebootSession(**stf.config.getIcebootOpts())

    def setup(self, test):
        # placeholder for OpenHTF setup phase
        #self.session.flashLS()
        #if self.session
        pass

    def tearDown(self, test):
        if self.session:
            INFO('tearing down session')
            try:
                self.session.reboot()
            except OSError:
                INFO('waiting for reboot...')
                time.sleep(3)
                del self.session
            INFO('done')

    # DEPRECATED
    def addTest(self, testCallable):
        self.tests.append(testCallable)

    # used for test sets
    def reconfigure(self, name, group, args, evs, config):
        self.test_name = name
        self._PARAMS['args'] = args
        self._PARAMS['expectedValues'] = evs
        self.group = group
        # ugh... don't wipe out testconfig settings stored in self.config
        self.config = stf.parse.update(self.config, config)
        stf.debug('reconfigure: ')
        stf.debug(config)

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

    ### TODO: implement option to ignore test "config" key? or at least iceboot
    #def execute(self, device, iceboot_config={'iceboot': {'host': 'localhost'}}):
    def execute(self, device, iceboot_config={'iceboot': {}}):
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

        # iceboot_config is provided by the framework and overrides test config settings

        # XXX: move this to seutp function or re-implement this as a plug?
        # hack for non-standard multiple tests run with single class
        self.session = getIcebootSession(**stf.config.getIcebootOpts())

        #if expected_values:
            #test_args['expectedValues'] = expected_values

        # add expectedValues directly to the measurement validator class
        for m in self.test_fn.measurements:
            for v in m.validators:
                setattr(v, 'expectedValues', expected_values)

        #self.session = getIcebootSession(**stf.config.getIcebootOpts())

        phases = [
            Common.checkCommsAndFirmware.with_args(session=self.session, 
                expectedValues={'expected_fw_vnum':stf.ENV.FIRMWARE_VERSION}),
            self.test_fn.with_args(session=self.session, **test_args)
            #run_test.with_plugs(session=IcebootSession).with_args(**test_args)
        ]

        T = htf.Test(htf.PhaseGroup(
                #setup=[self.setupIceboot],
                #setup=[self.setup],
                main=phases,
                teardown=[self.tearDown]
            ),
            # openhtf fields
            test_name=self.test_name,
            test_version=self.version,
            test_desc=self.desc,
            test_group='' if not self.group else f'{self.group}::',
            # custom metadata fields
            framework_version=stf.FRAMEWORK_VERSION,
            device=device,
            # XXX: make sure to include entire config eventually
            test_config=self._PARAMS,
            framework_override_config=self.config
        )
        #T.configure(teardown_function=self.tearDown)

        # XXX: how to deal with output options?
        T.add_output_callbacks(
            JSON(stf.ENV.JSONFILE_NAME, indent=4, default=str)
        )

        # XXX: add DEBUG flag?
        T.add_output_callbacks(
            console_summary.ConsoleSummary()
        )

        T.execute(test_start=lambda: device['id'])

        stf.dbg("finished execute for test: {}".format(self.test_name))
