from . import testclasses
import openhtf as htf
import stf

def __valid_test_name(x):
    return x is not None

def register(**kw):
    name = kw.get('test_name')
    if not name:
        import inspect
        frame = inspect.stack()[1]
        name = frame[0].f_code.co_filename.split('.')[0].split('/')[-1]
        stf.dbg('test_name not provided, using: {}'.format(name))
    if not __valid_test_name(name):
        raise Exception('Misconfigured test, invalid or missing `test_name`. Can not run')

    conf_file = kw.get('config_file')
    if not conf_file:
        stf.dbg('test name: ' + name)
        conf_file = '{}/{}.json'.format(stf.ENV.TEST_CONFIG_DIR, name)
        #conf_file = 'data/testconfig/{}.json'.format(kw['test_name'])

    version = kw.get('version')
    if not version:
        raise Exception('Misconfigured test, missing version. Will not run')


    # instantiate the class (optional param)
    _cls = kw.get('test_class', testclasses.MainboardTest)
    # test_function? or just run?
    func = kw.get('run')
    cls = _cls(version, name, test_fn=func, conf_file=conf_file)

    stf.addTestClass(cls)

    return True

# allows @stf.test decorator
def test(f):
    @htf.TestPhase()
    def deco(*args, **kw):
        return f(*args, **kw)
    # preserve original test name
    # XXX: functools here?
    try:
        deco.func.__name__ = f.__name__
        #deco.options.name = f.__name__
    except AttributeError:
        pass
    return deco


