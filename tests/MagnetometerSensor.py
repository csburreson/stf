# Test STMicroelectronics LIS3MDL Magnetometer, magnetic field sensor.
# Note the LIS3MDL includes an internal temperature sensor, which is covered be
# a different test.

# This test does not require a FPGA load.

# Though the magnitude of the magnetic field on the Earth's surfacde varies
# from 0.25 to 0.65 gauss, initial testing has shown the LIS3MDL can be
# influenced by nearby large metal objects, magnets, motors, etc. Accordingly,
# the pass/fail criteria are initially set to 3 x the max Earth field
# magnitude.

import stf
import numpy as np

# Derive a unique exception to indicate sensor I2C read error
class SensorI2CReadError(stf.STFException):
    pass

@stf.measures(stf.M('bField').expectRange('{bField_min}', '{bField_max}',
    type=float))
def run_test(test, session):
    # Test magnetometer read over I2C bus via python interface:
    bField = session.readMagnetometerXYZ() # Units: Tesla
    stf._PRINT(bField)
    if (bField is None):
        raise SensorI2CReadError('read LIS3MDL MagField error')
    vector = np.array(bField)
    magnitude = np.linalg.norm(vector)
    test.measurements.bField = magnitude
    # Convert Iceboot units gauss to SI units Tesla
    test.logger.info('Nominal Earth B field magnitude %g -> %g tesla' %
        (0.25/10000, 0.65/10000) )
    test.logger.info('Read magnetometer B field vector: [%g, %g, %g] tesla'
        % (bField[0], bField[1], bField[2]) )
    test.logger.info('Compute magnetometer B field magnitude: %g tesla' % (magnitude))

stf.register(
    # version should change if your code changes (required if this test has
    # been used in production). You're in charge of this version as a test
    # writer
    version='1.0',

    # run is required and points to the test function intended to be run
    run=run_test,

    # optional: test name is generated from filename if not provided
    test_name='Magnetometer',

    # optional: test_desc is a description of your test which will appear in
    # the output
    test_desc='LIS3MDL Magnetometer',
    # optional: defaults to std.testclasses.MainboardTest
    #test_class=stf.testclasses.MainboardTest,
    # override: use 'config_file' to point to a different location for config
    #   (default is STF_HOME/data/testconfig/<test_name>.json )
    # (if not provided, the framework would try to open "foo.json" with this
    # definition)
    config_file = 'data/testconfig/MagnetometerSensor.json',
)

# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
