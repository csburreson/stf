import test as I3Test

class FWVersionTestPhases(I3Test.MainboardTest):
    @I3Test.measures(
        I3Test.M('fw_vnum').equalsParam('expected_fw_vnum')
    )
    def fw_vnum_test(test, session, expected_fw_vnum):
        test.measurements.fw_vnum = hex(session.fpgaVersion())

    @I3Test.measures(
        I3Test.M('foobar').in_range('{min}', '{max}', type=int)
    )
    def foo(test, session, min, max):
        test.measurements.foobar = 42

# should inherit from MainboardTest
# and ALSO requires that "Test" be in the classname
class FWVersionTest(I3Test.MainboardTest):
    # REQUIRED: VERSION field (use in output)
    VERSION = "1.0"

    # params field is OPTIONAL
    #   it's a dictionary of 'method_name' => listOfParamNames
    # 
    # if desired... could expand listOfParamNames to include 
    # param type?
    PARAMS = {
        'fw_vnum_test': ['expected_fw_vnum'],
        'foo': ['min', 'max']
    }

    # use config to override iceboot settings
    # NOTE: not sure if we'll need to keep CONFIG as is...
    # OPTIONAL
    '''
    CONFIG = {
        'iceboot': {
            'fpgaConfigurationFile': 'xxx.rbf',
            'host': '192.168.0.10',
            'port': 5012
            'debug': False
        }
    }
    '''

    # REQUIRED: TESTS is a list of callables (functions) 
    TESTS = [
        FWVersionTestPhases.fw_vnum_test, 
        FWVersionTestPhases.foo
    ]

I3Test.run() 
