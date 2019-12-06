import stf as I3Test
from os.path import join

class FWVersionTestPhases(I3Test.MainboardTest):
    @I3Test.measures(
        I3Test.M('fw_vnum').equalsParam('expected_fw_vnum')
    )
    def fw_vnum_test(test, session, expected_fw_vnum):
        test.measurements.fw_vnum = hex(session.fpgaVersion())

    # collapse this into a single decorator? 
    @I3Test.measures(
        I3Test.M('foobar').in_range('{foo_min}', '{foo_max}', type=int)
    )
    def foo(test, session, foo_min, foo_max):
        test.measurements.foobar = 42


'''
a "runnable" I3Test must descend from I3Test.Test

Propertires should include:

VERSION = <str>
TESTS = <list>
    list contains callables (functions)
'''
# XXX: collapse runnable and configure into a single decorator?
'''
@I3Test.runnable(  # or just "register(" ?
    # in the future, we can automatically query
    varFile='path/to/vars.json',
    version='1.0.0',
    desc='optional; fallback to docstring',
)
'''
# runnable registers this test
@I3Test.register(
    config_file=join(I3Test.DB_DIR, 'testconf/fwvars.json'),
    version='1.0'
)
# set params
#@I3Test.configure(join(I3Test.DB_DIR, 'testconf/fwvars.json'))
class FWVersionTest(I3Test.MainboardTest):
    VERSION = "1.0"
    DESC = ("optional test description. if not provided, "
            "fallback to docstring or nothing")

    # params field is OPTIONAL
    #   it's a dictionary of 'method_name' => listOfParamNames
    # 
    # if desired... could expand listOfParamNames to include 
    # param type?
    '''
    PARAMS = {
        'fw_vnum_test': ['expected_fw_vnum'],
        'foo': ['min', 'max']
    }
    '''

    # use config to override iceboot settings
    # NOTE: not sure if we'll need to keep CONFIG as is...
    # OPTIONAL
    CONFIG = {
        'iceboot': {
            'fpgaConfigurationFile': 'fw_0x6a.rbf',
            #'host': '192.168.0.10',
            'port': 5012,
            'host': 'localhost'
        }
    }
    '''
    '''

    # REQUIRED: TESTS is a list of callables (functions) 
    TESTS = [
        FWVersionTestPhases.fw_vnum_test, 
        FWVersionTestPhases.foo
    ]

if __name__ == '__main__':
    I3Test.run() 
