# Jim Braun
#
# Tests that interlocks have the expected values
#

import stf


@stf.measures(stf.M('flashInterlock').equals('flashInterlockValue}'),
              stf.M('configInterlock').equals('configInterlockValue}'),
              stf.M('hvInterlock').equals('hvInterlockValue}'),
              stf.M('lidInterlock').equals('lidInterlockValue}'))
def run_test(test, session):
    test.measurements.flashInterlock = session.readFlashInterlock()
    test.measurements.configInterlock = session.readFPGAConfigInterlock()
    test.measurements.hvInterlock = session.eadHVInterlock()
    test.measurements.lidInterlock = session.readLIDInterlock()


stf.register(
    version='1.0',
    test_name='Interlock',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
