import json
import time
import openhtf as htf
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.output.callbacks import console_summary
from .core import getIcebootSession
from .validators import *
import stf
from .util.colors import termcolor as clr
from .util.misc import INFO, check_mainboard_fwfile, getTimeSlug
from .util import files
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
            gINFO(f'checkCommsAndFirmware -> configuring fw file from flash: {paths.fwfile_name})')
        elif fwfile_status == 'skip':
            gINFO(f'checkCommsAndFirmware -> SKIPPING fw file upload, configuring: {paths.fwfile_name}')
        else:
            gINFO(f'checkCommsAndFirmware -> uploading fw file to flash: {paths.fwfile}... \n\t(this could take a while)')
            session.ymodemFlashUpload(paths.fwfile_name, paths.fwfile)

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
        self.tests = []
        self.group = kw.get('group', '')
        self.group_timeslug = kw.get('group_timeslug', '')

        # optional description
        self.desc = kw.get('test_desc') or 'n/a; see test file: {}'.format(test_name)

        # test_params is a map of fn name = list of varnames
        #self.test_params = kw.get('params', {})
        self.test_name = test_name
        if not callable(test_fn):
            raise Exception('Invalid "test_fn" parameter. Expecting callable')
        self.test_fn = test_fn
        self.version = version
        # instance can be none
        self.instance = kw.get('instance', 'base')

        stf.dbg('creating MainboardTest class for: {}:{}'.format(test_name, self.instance))

        #self.session = None
        # XXX: move to init or "configure" step or something
        self.config = Common.TEST_CONFIG
        conf_file = kw['conf_file']

        # for instance derivations, args and evs are already figured out from base instance
        # and passed directly here
        if self.instance != 'base':
            self._PARAMS = {
                'args': kw.get('instance_args', {}),
                'expectedValues': kw.get('instance_expectedValues', {})
            }
            return

        # skip loading config (note that instance derivations use stf.NOCONFIG)
        if conf_file == stf.NOCONFIG:
            self._PARAMS = {'args': {}, 'expectedValues': {}}
            self._PARAM_CONF_FILE = None
            return


        # load config (base instances only)
        conf_file_path = files.getFilePath(conf_file)
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

    # Process any queued MCU internal logging records
    def logOutput(self, test):
        logOutputLines = self.session.printLogOutput()
        if len(logOutputLines) == 0:
            return
        logOutput = logOutputLines.split('\r\n')
        for logLine in logOutput:
            if len(logLine) == 0:
                # Weird: split of empty multiline string produces nonzero number of strings
                continue;
            word = logLine.split()
            logFn = test.logger.error
            # Map MCU logging level to test logging level
            if len(word) == 0:
                continue
            if word[0] == 'DEBUG':
                logFn = test.logger.info
            elif word[0] == 'INFO':
                logFn = test.logger.info
            logFn('MCU log: ' + logLine)


    def tearDown(self, test):
        if self.session:
            if hasattr(self.session, 'FAKE'):
                return
            self.logOutput(test)
            INFO('tearing down ... initiating reboot()')
            # XXX:rebootafter
            try:
                self.session.reboot()
            except (OSError, IOError):
                stf.debug('oserror thrown by reboot (expected)')
                del self.session
            stf.debug('teardown complete')

    # DEPRECATED
    def addTest(self, testCallable):
        self.tests.append(testCallable)

    # used for test sets
    def reconfigure(self, name, group, args, evs, timeslug='', config={}):
        self.instance = name
        self._PARAMS['args'] = args
        self._PARAMS['expectedValues'] = evs
        self.group = group
        # used for output
        self.group_timeslug = timeslug
        # ugh... don't wipe out testconfig settings stored in self.config
        #self.config = stf.parse.update(self.config, config)
        stf.debug(f'reconfigure: {config}')

    def deriveInstance(self, name, group, args, evs, timeslug='', config={}):
        if (name == 'base'):
            self.group = group
            self.group_timeslug = timeslug
            return self

        return type(self)(self.version, self.test_name, self.test_fn, 
            test_desc=self.desc, group=group, group_timeslug=timeslug,
            instance=name, instance_args=args, instance_expectedValues=evs,
            conf_file=stf.NOCONFIG
        )

    def getTestParams(self):
        '''
        self._PARAMS is dict of {
        }
        '''
        # XXX: this requires @configure deco
        if hasattr(self, '_PARAMS'):
            return self._PARAMS

        #return ParamDB.getTestParams(pname, plist)
        return {}
    
    def get_session(self):
        return self.session

    ### TODO: implement option to ignore test "config" key? or at least iceboot
    def execute(self, device, config={}):
        # could we get params from the fn itself and possibly declare them with
        # defaults with a decorator, eliminating the need for a testconfig
        # file? if so, would it buy us much? probably not
        inst = config.get('instance', {})
        if inst:
            test_args = inst.get('args', {})
            expected_values = inst.get('expectedValues', {})
            group = inst['group']
            group_timeslug = inst['group_timeslug']
            instance_name = inst['instance']
        else:
            ps = self.getTestParams()
            test_args = ps.get('args', {})
            expected_values = ps.get('expectedValues', {})
            group = ''
            group_timeslug = ''
            instance_name = 'base'

        x = config.get('iceboot', {})
        dut_host = x.get('host') or stf.config.settings.iceboot.host
        dut_port = x.get('port') or stf.config.settings.iceboot.port

        # TODO: get test desc (or keep this in DB and link to test name)
        desc = 'todo'

        stf.dbg('test args: {}'.format(test_args))
        stf.dbg('expected values: {}'.format(expected_values))

        # XXX: move this to seutp function or re-implement this as a plug?
        #try:
        self.session = getIcebootSession(host=dut_host, port=dut_port)
        #except:
        #    self.session = None
        #    stf.dbg('Lots of OSErrors... sleeping for 10...')
        #    time.sleep(10)
        #    self.session = getIcebootSession(host=dut_host, port=dut_port)

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
            # XXX: self.desc could be mentioned in setconfig
            test_desc=self.desc,
            test_instance=instance_name,
            # HEY: test_group is referenced by config
            # HEY: test_group is referenced by runset/scripts
            test_group=group,
            test_config={
                'args': test_args,
                'expectedValues': expected_values
            },
            # custom metadata fields
            stf_version=stf.FRAMEWORK_VERSION,
            stf_config=stf.config.settings.dict(),
            device=device,
            conn=config.get('iceboot', {})
        )
        #T.configure(teardown_function=self.tearDown)

        output = stf.config.settings.output
        if output.json.enabled:
            # issue X: support timeSlugs in path 
            p = files.join(
                stf.config.get_path('json_results'),
                # this can be empty str
                group,
                group_timeslug,
                output.json.filename
            )
            stf.debug(f'jsonout path: {p}')
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
