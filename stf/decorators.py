from . import testclasses
import openhtf as htf
import stf

def __valid_test_name(x):
    # XXX: define valid test name (a-zA-Z0-9 and "-", ".", "_")?
    return x is not None

# XXX: no longer a decorator... should be in core?
def register(**kw):
    '''
    this function registers a given test with the framework

    required kwargs:
        version 
            string denoting the version of this test (in case it's run in
            production and then modified)

        run 
            pass in the test function here.
    
    optional kwargs:
        test_name 
            by default, the framework will attempt to use the name of
            the file from which register was called.

        config_file 
            by default, the framework will look for a a "testconfig"
            directory containing the tests config file:
            i.e. os.join(stf.ENV.DATA_DIR, 'testconfig', '<test_name>.json')
            or "$STF_HOME/data/testconfig/test_name.json" where STF_HOME
            is the location of the stf package

        test_class
            by default, the framework will use 'stf.tests.MainboardTest' as the
            testClass
    '''
    name = kw.get('test_name')
    import inspect
    frame = inspect.stack()[1]
    stf.dbg(frame)
    if not name:
        from .util.files import getNameFromPath
        name = getNameFromPath(frame[0].f_code.co_filename)
        stf.dbg('test_name not provided, using: {}'.format(name))
    if not __valid_test_name(name):
        raise Exception('Misconfigured test, invalid or missing `test_name`. Can not run')

    try :
        frame = inspect.stack()[2]
        testLocals = frame[0].f_locals
        testGlobals = frame[0].f_globals
        code_obj = frame[0].f_code
    except IndexError:
        testLocals = {}
        testGlobals = {}
        code_obj = None
        pass
    #stf.dbg('testLocals: {}'.format(testLocals))

    if '__STF_TEST_OVERRIDES' in testLocals:
        stf.dbg('TEST OVERRIDES FOUND')

    conf_file = kw.get('config_file')
    if not conf_file:
        stf.dbg('config_file not provided for test: ' + name)
        conf_file = '{}/{}.json'.format(stf.ENV.TEST_CONFIG_DIR, name)
        stf.dbg('trying {}'.format(conf_file))
        # XXX: validate config here, raise Exception

    version = kw.get('version')
    if not version:
        raise Exception('Misconfigured test, missing version. Will not run')


    # instantiate the class (optional param)
    _cls = kw.get('test_class', testclasses.MainboardTest)
    # test_function? or just run?
    func = kw.get('run')
    if not hasattr(func, 'measurements'):
        func = make_test(func)
    # XXX: func.func.__globals?
    #testLocals['STF_RUN_TEST'] = func
    #func.func.__globals__.update(testLocals)
    #stf.dbg('testLocals {}'.format(testLocals.keys()))
    #stf.dbg('testGlobals{}'.format(testGlobals.keys()))
    #func.func.__locals__.update(testLocals)

    desc = kw.get('test_desc')
    # get test description from the function's docstring if test_desc is not present
    #desc = desc or func.__doc__
    cls = _cls(version, name, test_fn=func, conf_file=conf_file, test_desc=desc)

    stf.addTestClass(name, cls, testLocals, testGlobals, code_obj=code_obj)

    return True

# allows @stf.test decorator
def make_test(f):
    @htf.TestPhase()
    def deco(*args, **kw):
        return f(*args, **kw)
    # preserve original test name
    # XXX: functools here?
    try:
        deco.func.__name__ = f.__name__
        deco.func.__doc__ = f.__doc__
        deco.registered = True
        #deco.options.name = f.__name__
    except AttributeError:
        pass
    return deco
