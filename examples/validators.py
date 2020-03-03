import stf

'''this test is meant to fail on the last measurement and demonstrated validators'''

@stf.measures(
    # notice the type is required for ints and string ranges
    stf.M('flux').expectRange('{foo}', '{bar}', type=int),
    stf.M('peak').expect('{peak}', type=int),
    stf.M('grooviness').expectRange('{groove_low}', '{groove_high}', type=str),
    stf.M('status').expect('{ok_status}'),
    stf.M('str').expectRegex('{somepattern}'),
    # no type required for percentages (int/float assumed)
    stf.M('percent').expectPercent('{expectedVal}', '{percent}'),
    stf.M('percentFail').expectPercent('{expectedVal}', '{percent}'),
    stf.M('percentFailNone').expectPercent('{expectedVal}', '{percent}')
)
def run_test(test, session):
    test.measurements.flux = 42
    test.measurements.peak = 4422
    test.measurements.str = 'deadbeef'
    test.measurements.status = 'OK'
    test.measurements.grooviness = 'groovtastic'

    test.measurements.percent =  950

    # THIS measurement fails:
    test.measurements.percentFail = 899

    # THIS measurement fails (but does not raise exception)
    test.measurements.percentFailNone = None


# register decorator accepts version and config file
stf.register(
    version='1.0',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
