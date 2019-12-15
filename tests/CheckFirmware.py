import stf

@stf.measures(stf.M('fw_vnum').equalsParam('expected_fw_vnum'))
def run_test(test, session, expectedValues):
    '''this test simply checks the expected firmware version'''
    fw_version = hex(session.fpgaVersion())
    test.logger.info('Got fw version: {}'.format(fw_version))
    test.measurements.fw_vnum = fw_version
    

stf.register(
    # version should change if your code changes (required if this test has
    # been used in production)
    version='1.0',
    # just use this file's filename
    test_name='CheckFirmware',
    run=run_test,
)

# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
