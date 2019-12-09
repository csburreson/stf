from . import testclasses
import stf

def __valid_test_name(x):
    return True

def register(**kw):
    global TESTABLE_CLASSES

    conf_file = kw.get('config_file')
    if not conf_file:
        conf_file = 'data/testconfig/{}.json'.format(kw['test_name'])

    version = kw.get('version')
    if not version:
        raise Exception('Misconfigured test, missing version. Will not run')

    name = kw.get('test_name')
    if not __valid_test_name(name):
        raise Exception('Misconfigured test, invalid or missing `test_name`. Can not run')

    # instantiate the class (optional param)
    _cls = kw.get('test_class', testclasses.MainboardTest)
    # test_function? or just run?
    func = kw.get('run')
    cls = _cls(version, name, test_fn=func, conf_file=conf_file)

    TESTABLE_CLASSES.append(cls)

    return True

# allows @stf.test decorator
def test(f):
    @htf.TestPhase()
    def deco(*args, **kw):
        return f(*args, **kw)
    # preserve original test name
    deco.func.__name__ = f.__name__
    deco.options.name = f.__name__
    return deco
