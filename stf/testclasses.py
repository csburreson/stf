class TestSet(object):
    def __init(self, version):
        pass

class Common:
    # default test config options
    TEST_CONFIG = {
        'timeout_s': 10
    }
    # decorate this as a test?
    def checkCommsAndFirmware(test, session):
        pass

class MainboardTest(object):
    def __init__(self, version, test_name, test_fn=None, **kw):
        self.tests = []


        # not needed? 
        self.config = kw.get('config', {})

        # test_params is a map of fn name = list of varnames
        self.test_params = kw.get('params', {})
        self.test_name = test_name
        if not callable(test_fn):
            raise Exception('Invalid "test_fn" parameter. Expecting callable')
        self.test_fn = test_fn
        self.version = version
        # instance can be none
        self.instance = kw.get('instance')

        # XXX: move to init or "configure" step or something
        conf_file = kw['conf_file']
        with open(conf_file, 'r') as f:
            #dbg("(@configure) loaded {}".format(conf_file))
            cls._PARAMS = json.load(f)
            cls._PARAM_CONF_FILE = conf_file
            #dbg("(@configure) {}".format(cls._PARAMS))
            raise Exception('Misconfigured test, missing version')

        # XXX:
        # create iceboot session here?
        # or as a test phase?
    def setupIceboot(self):
        self.session = stf.getIcebootSession(fake=FAKE_ICEBOOT,
            **self.config.get('iceboot', {})
        )

    # DEPRECATED
    def addTest(self, testCallable):
        self.tests.append(testCallable)

    def getTestParams(self, pname):
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
            return self._PARAMS.get(pname, {})

        if not getattr(self, 'test_params') or not self.test_params:
            return {} 

        #pname = func
        if pname not in self.test_params:
            return {}

        # lookup param values
        plist = self.test_params[pname]
        get_db()
        return ParamDB.getTestParams(pname, plist)
    
    def execute(self, device):
        # could we get params from the fn itself and possibly declare them with
        # defaults with a decorator, eliminating the need for a testconfig
        # file? if so, would it buy us much? probably not
        self._PARAMS = ps = self.getTestParams(self.test_name)

        # could get device config here:
        # dev_conf = getDeviceConfig(device)

        # TODO: get test desc (or keep this in DB and link to test name)
        desc = 'todo'

        # get test arguments (from json file)
        test_args = ps.get('args', {})

        # get test configuration options (defaults hardcoded, override in test config file
        # with "conf" top-level key
        defaults = testclasses.Common.TEST_CONFIG
        test_conf = defaults.update(ps.get('conf', {}))

        phases = [
            setup_iceboot.with_args(session=self.session),
            Common.checkCommsAndFirmware.with_args(session=self.session),
            run_test.with_args(session=self.session).with_args(**test_args)
            #run_test.with_plugs(session=IcebootSession).with_args(**test_args)
        ]

        T = htf.Test(
            *phases,
            # openhtf fields
            test_name=self.test_name,
            test_version=self.version,
            test_desc=desc or 'no description',
            # custom metadata fields
            framework_version=FRAMEWORK_VERSION,
            device=device,
            testOptions={
                'params': test_args
            }
        )

        T.add_output_callbacks(
            JSON(OUTPUT_JSONFILE, indent=4, default=str)
        )

        # get session here???
        #T.session = getIcebootSession(fake=FAKE_ICEBOOT,
        #    self.CONFIG.get)
        T.execute(test_start=lambda: device['id'])



    def executeOLD(self, device):
        # test disco?
        try:
            self.tests = self.TESTS
        except AttributeError:
            print "Error! No TESTS property found"
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
                    dbg('CHECKPOINT')
                    phases.append(x)
                    continue
                args = self.getTestParams(fn_name)
                test_args[fn_name] = args

                dbg(fn_name)
                #dbg('{}.{}'.format(self.__class__.name, fn_name))
                dbg('optname: {}'.format(x.options.name))
                phases.append(x.with_args(session=self.session, **args))
            except AttributeError:
                # XXX
                dbg('AttrErr')
                #x = test(x)
                phases.append(x)

#.with_args(T, T.meta, T.measurements, {}),

        phases = [test_fn]
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
