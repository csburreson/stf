import stf

@stf.measures(stf.M('fw_vnum').equalsParam('expected_fw_vnum'))
def run_test(test, session, **kw):
    # see tests/template.json for testconfig
    test.measurements.fw_vnum = hex(session.fpgaVersion())


stf.register(
    # version should change if your code changes (required if this test has
    # been used in production)
    version='1.0',
    # just use this file's filename
    #test_name=__file__.split('.')[0].split('/')[-1],
    run=run_test,
    #testClass=stf.testclasses.MainboardTest,
)

# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
