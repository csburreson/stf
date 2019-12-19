# Jim Braun
#
# Tests that interlocks have the expected values
#

import stf


@stf.measures(stf.M('flashInterlock').equalsParam('flashInterlockValue}', type=bool),
              stf.M('configInterlock').equalsParam('configInterlockValue}', type=int),
              stf.M('hvInterlock').equalsParam('hvInterlockValue}', type=bool),
              stf.M('lidInterlock').equalsParam('lidInterlockValue}', type=bool))
def run_test(test, session):
    test.measurements.flashInterlock = session.readFlashInterlock()
    test.measurements.configInterlock = session.readFPGAConfigInterlock()
    test.measurements.hvInterlock = session.readHVInterlock()
    test.measurements.lidInterlock = session.readLIDInterlock()


stf.register(
    version='1.0',
    test_name='Interlock',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
