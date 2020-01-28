import json
import time
import openhtf as htf
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.output.callbacks import console_summary
from .core import getIcebootSession
from .validators import *
import stf
from .util.colors import termcolor as clr
from .util.misc import INFO, check_mainboard_fwfile
from .util.files import getFilePath
FAKE_ICEBOOT = False

# class TestSet(object):




class Common(object):
    # default test config options
    TEST_CONFIG = {
        'timeout_s': 10
    }
    @stf.measures(
        stf.M('fpgaVersion').equals(stf.config.settings.iceboot.fw_version),
        stf.M('softwareId'),
        stf.M('softwareVersion')
    )
    #XXX: need long timeout for localhost from crappy inet cnxn
    @stf.options(timeout_s=500)
    def checkCommsAndFirmware(test, session, **kw):
        gINFO = stf.ginfo(['framework', 'iceboot'])
        vn = session.fpgaVersion()
        stf.dbg('running framework FW test, got vn: {} (expecting {})'.format(hex(vn), kw['expectedValues']['expected_fw_vnum']))

        paths = stf.config.settings.paths

        flash = session.flashLS()

        try:
            fwfile_status = check_mainboard_fwfile(flash)
        except FileNotFoundError as e:
            gINFO(f'FW File does not exist: {e}')
            return stf.STOP

        gINFO(f'checking flash for {paths.fwfile} ... status={fwfile_status})')

        if fwfile_status == 'ok':
            gINFO(f'checkCommsAndFirmware -> configuring fw file from flash: {paths.fwfile_remote})')
        elif fwfile_status == 'skip':
            gINFO(f'checkCommsAndFirmware -> SKIPPING fw file upload, configuring: {paths.fwfile_remote}')
        else:
            gINFO(f'checkCommsAndFirmware -> uploading fw file to flash: {paths.fwfile}... \n\t(this could take a while)')
            session.ymodemFlashUpload(paths.fwfile, paths.fwfile_name)

        session.flashConfigureCycloneFPGA(paths.fwfile_name)

        vn = session.fpgaVersion()
        test.measurements.fpgaVersion = hex(vn)
        if vn == 0xFFFF:
            test.logger.error('unable to configure firmware. quitting.')
            gINFO('unable to configure firmware. quitting.')
            return stf.STOP

        test.measurements.softwareId = session.softwareId()
        test.measurements.softwareVersion = session.softwareVersion()

        x = test.measurements
        stf.debug(f'FPGA v{vn} Configured. IceBoot v{x.softwareVersion} git: {x.softwareId}')
        stf.debug('Starting main test phase...')


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
        self.instance = kw.get('instance', 'base')

        #self.session = None
        # XXX: move to init or "configure" step or something
        self.config = Common.TEST_CONFIG
        conf_file = kw['conf_file']

        # skip loading config
        if conf_file == stf.NOCONFIG:
            self._PARAMS = {'args': {}, 'expectedValues': {}}
            self._PARAM_CONF_FILE = None
            return

        conf_file_path = getFilePath(conf_file)
        if not conf_file_path:
            # TODO: STFException -> STFTestConfigException
            raise Exception('TestConfigException: config file not found {conf_file}')

        with open(conf_file_path, 'r') as f:
            try:
                self._PARAMS = stf.parse.json_load(f)
            except json.decoder.JSONDecodeError:
                raise Exception('Invalid test configuration file! Is this valid JSON?')
            self._PARAM_CONF_FILE = conf_file_path
            #if 'config' in self._PARAMS:
            #    cfg = self._PARAMS['config']
                #stf.dbg('configure: config overrides: {}'.format(cfg))
                # XXX: should we do this anymore? for test timeouts maybe?
            #    self.config.update(cfg)
                #stf.dbg('configure: full config: {}'.format(self.config))

        if not 'args' in self._PARAMS:
            self._PARAMS['args'] = {}

        if not 'expectedValues' in self._PARAMS:
            self._PARAMS['expectedValues'] = {}

    def __del__(self):
        #if self.session:
        #    del self.session
        #    time.sleep(3)
        pass

    # create iceboot session here? or as a test phase?
    def setupIceboot(self, test):
        #if session:
        #    INFO("HERE")
        #    del self.session
        #    import time
        #    time.sleep(5)
        self.session = getIcebootSession()

    def setup(self, test):
        # placeholder for OpenHTF setup phase
        #self.session.flashLS()
        #if self.session
        pass

    def tearDown(self, test):
        if self.session:
            if hasattr(self.session, 'FAKE'):
                return
            INFO('tearing down ... initiating reboot()')
            # XXX:rebootafter
            try:
                self.session.printLogOutput()
                self.session.reboot()
            except OSError:
                stf.debug('oserror thrown by reboot (expected)')
                del self.session
            stf.debug('teardown complete')

    # DEPRECATED
    def addTest(self, testCallable):
        self.tests.append(testCallable)

    # used for test sets
    def reconfigure(self, name, group, args, evs, config):
        self.instance = name
        self._PARAMS['args'] = args
        self._PARAMS['expectedValues'] = evs
        self.group = group
        # ugh... don't wipe out testconfig settings stored in self.config
        self.config = stf.parse.update(self.config, config)
        stf.debug(f'reconfigure: {config}')

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

        # XXX: move this to seutp function or re-implement this as a plug?
        # hack for non-standard multiple tests run with single class
        self.session = getIcebootSession()

        # XXX:rebootfirst
        '''
        try:
            stf.debug('rebooting device...')
            self.session.reboot()
            stf.debug("POST REBOOT")
            time.sleep(5)
            stf.debug("REBOOT POST FSLEEP")
        except OSError:
            stf.debug("NEW SESSION")
            #del self.session
            #del self.session
            time.sleep(2)
            self.session = getIcebootSession(**stf.config.getIcebootOpts())
        '''

        #if expected_values:
            #test_args['expectedValues'] = expected_values

        # add expectedValues directly to the measurement validator class
        for m in self.test_fn.measurements:
            for v in m.validators:
                setattr(v, 'expectedValues', expected_values)

        phases = [
            Common.checkCommsAndFirmware.with_args(session=self.session, 
                expectedValues={'expected_fw_vnum':stf.config.settings.iceboot.fw_version}),
            self.test_fn.with_args(session=self.session, **test_args)
            #run_test.with_plugs(session=IcebootSession).with_args(**test_args)
        ]

        T = htf.Test(htf.PhaseGroup(
                main=phases,
                teardown=[self.tearDown]
            ),
            # openhtf fields
            test_name=self.test_name,
            test_version=self.version,
            test_desc=self.desc,
            test_instance=self.instance,
            # HEY: test_group is referenced by config
            # HEY: test_group is referenced by runset/scripts
            # XXX: this breaks non-linux environments :shrug:
            test_group='' if not self.group else f'{self.group}/',
            test_config=self._PARAMS,
            # custom metadata fields
            stf_version=stf.FRAMEWORK_VERSION,
            stf_config=stf.config.settings.dict(),
            # 
            device=device,
        )
        #T.configure(teardown_function=self.tearDown)

        output = stf.config.settings.output
        if output.json.enabled:
            p = stf.config.get_path('json_output', filename=output.json.filename)
            T.add_output_callbacks(
                JSON(p, indent=4, default=str)
            )

        if output.console.enabled:
            T.add_output_callbacks(
                console_summary.ConsoleSummary()
            )

        T.execute(test_start=lambda: device['id'])
        '''
        INFO(f'{dir(T)}')
        T.descriptor.metadata['board_fpgaVersion'] = session.fpgaVersion
        T.descriptor.metadata['board_softwareVersion'] = session.fpgaVersion
        T.descriptor.metadata['board_softwareId'] = session.fpgaVersion
        '''
        #self.T = T

        INFO(f'Finished {self.test_name}')
        stf.dbg("finished execute for test: {}".format(self.test_name))
