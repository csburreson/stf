from . import testclasses
import openhtf as htf
import stf

def __valid_test_name(x):
    return x is not None

def register(**kw):
    name = kw.get('test_name')
    if not __valid_test_name(name):
        raise Exception('Misconfigured test, invalid or missing `test_name`. Can not run')

    conf_file = kw.get('config_file')
    if not conf_file:
        conf_file = '{}/{}.json'.format(stf.env.TEST_CONFIG_DIR, name)
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
    deco.func.__name__ = f.__name__
    deco.options.name = f.__name__
    return deco


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
        return type(self)(
            pvalue=htf.util.format_string(self.paramValue, kw),
            type=kw.get('type', None),
        )
