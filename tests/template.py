import stf

@stf.measures(stf.Measurement('xxx').equalsParam('{foo}'))
def run_test(test, session, arg1=None, **kw):
    # see tests/template.json for testconfig
    test.measurements.xxx = 'bar' 

    if arg1 is None:
        test.logger.error('misconfigured arg!')
        return stf.FAIL
    else:
        test.logger.info('Got arg1: {}'.format(arg1))

    # OK if we get here, framework takes care of comparing xxx to bar


stf.register(
    # version should change if your code changes (required if this test has
    # been used in production)
    version='1.0',
    # test name is required and XXX: test_slug and test_name? test_name is pretty for humans and slug is suitable for filenames, etc?
    test_name='foo',
    run=run_test,
    testClass=stf.testclasses.MainboardTest,
)

# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
