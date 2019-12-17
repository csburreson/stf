import stf

@stf.measures(
    stf.M('flux').expectRange('{foo}', '{bar}', type=int),
    stf.M('peak').expect('{bar}', type=int),
    stf.M('str').expectRegex('{somepattern}'),
    stf.M('percent').expectPercent('{expectedVal}', '{percent}'),
    stf.M('percentFail').expectPercent('{expectedVal}', '{percent}')
   # , '^somestringVal$'),
)
def run_test(test, session):
    test.measurements.flux = 42
    test.measurements.peak = 44
    test.measurements.str = 'deadbeef'

    test.measurements.percent =  950
    test.measurements.percentFail = 899


# register decorator accepts version and config file
stf.register(
    version='1.0',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
