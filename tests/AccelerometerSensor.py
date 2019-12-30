import stf
import numpy as np

@stf.measures(stf.M('accel_mag').expectRange('{accel_mag_min}', '{accel_mag__max}', type=float))
def run_test(test, session):
    # Test magnitude of acceleration read over I2C bus via python interface:
    #  session.readAccelerometerXYZ()
    my_accel = session.readAccelerometerXYZ()
    my_accel_mag = np.sqrt(my_accel[0]*my_accel[0] + my_accel[1]*my_accel[1] + my_accel[2]*my_accel[2])
    test.measurements.accel_mag = my_accel_mag
    test.logger.info('Read accelerometer: {}, Magnitude: {}'.format(my_accel,my_accel_mag))

stf.register(
    # version should change if your code changes (required if this test has
    # been used in production). You're in charge of this version as a test writer
    version='1.0',

    # run is required and points to the test function intended to be run
    run=run_test,

    # optional: test name is generated from filename if not provided
    test_name='AccelerometerSensor',
    # optional: test_desc is a description of your test which will appear in the output
    test_desc='Test temperature sensor on Accelerometer Sensor ADXL355',
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
