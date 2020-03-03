import stf
import numpy as np

@stf.measures(stf.M('accel_z').expectRange('{accel_z_min}', '{accel_z_max}', type=float))
def run_test(test, session):
    # Test direction of acceleration read over I2C bus via python interface:
    #  session.readAccelerometerXYZ()
    # In other workds, make sure the MB is flat and right-side up...
    my_accel = session.readAccelerometerXYZ()
    test.measurements.accel_z = my_accel[2]
    test.logger.info('Read z accelerometer magnitude: {}'.format(my_accel[2]))

stf.register(
    # version should change if your code changes (required if this test has
    # been used in production). You're in charge of this version as a test writer
    version='1.0',

    # run is required and points to the test function intended to be run
    run=run_test,

    # optional: test name is generated from filename if not provided
    test_name='MBOrientation',
    # optional: test_desc is a description of your test which will appear in the output
    test_desc='Test magnitude and direction of z-compoenent of accelerometer',
    # optional: defaults to std.testclasses.MainboardTest
    test_class=stf.testclasses.MainboardTest,
    # override: use 'config_file' to point to a different location for config
    #   (default is STF_HOME/data/testconfig/<test_name>.json )
    # (if not provided, the framework would try to open "foo.json" with this definition)
    config_file=None
)

# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
