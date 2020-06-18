import stf

# Derive a unique exception to indicate sensor I2C read error
class SensorI2CReadError(stf.STFException):
    pass

@stf.measures(stf.M('temp').expectRange('{temp_min}', '{temp_max}', type=float))
def run_test(test, session):
    # Test temperature read over I2C bus via python interface:
    #  session.readAccelerometerTemperature()
    my_temp = session.readAccelerometerTemperature()
    if (my_temp is None):
        raise SensorI2CReadError('read ADXL355 temperature error')
    test.measurements.temp = my_temp
    test.logger.info('Read pressure sensor temp: {}'.format(my_temp))

stf.register(
    # version should change if your code changes (required if this test has
    # been used in production). You're in charge of this version as a test writer
    version='1.0',

    # run is required and points to the test function intended to be run
    run=run_test,

    # optional: test name is generated from filename if not provided
    test_name='TempAccelerometerSensor',
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
