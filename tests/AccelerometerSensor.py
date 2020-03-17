# Test ADXL355 accelerometer. Notes: reads can fail if the I2C bus is hung and
# unrecoverable. The ADXL355 is sensitive to local vibrations. More below.
import stf
import numpy as np
import statistics
import math
import time

Me = 'AccelerometerSensor'

# Derive a unique exception to indicate sensor I2C read error
class SensorI2CReadError(stf.STFException):
    pass


# The ADXL355 acceleromoter is sensitive to local vibration. Testing has shown
# detection of acceleration magnitude ranging 7 <= a <= 13 m/s^2, and
# inclinations ranging 0 <= i <= 10 degrees. Read the accelerometer multiple
# times attempting to disqualify values due to vibration.
@stf.measures(stf.M('accel_mag').expectRange(
    '{accel_mag_min}', '{accel_mag_max}', type=float))
@stf.measures(stf.M('inclination').expectRange(
    '{inclination_min}', '{inclination_max}', type=float))
def run_test(test, session, samples_min=1, max_reads=20):
    time_start = time.time()
    expectedValues = stf.getRegisteredClass(Me)._PARAMS['expectedValues']
    accel_mag_min = expectedValues['accel_mag_min']
    accel_mag_max = expectedValues['accel_mag_max']
    samples = []
    mags = []
    for read in range(max_reads):
        sample = session.readAccelerometerXYZ()

        if (sample is None):
            raise SensorI2CReadError('read ADXL355 acceleration error')

        # Compute acceleration magnitude. Discard out of limit readings due to
        # assumed vibrations.
        mag = np.linalg.norm(sample)
        if mag < accel_mag_min or mag > accel_mag_max:
            test.logger.info("Rejecing acceleration reading ",
                sample, " magnitude %g limit error" % (mag))
            continue

        samples.append(sample)
        mags.append(mag)
        if len(samples) >= samples_min:
            break

    # Find median magnitude value. median_low() returns always returns a value
    # in the set, and does not average values in an even numbered set
    median = None
    try:
        median = statistics.median_low(mags)
    except statistics.StatisticsError:
        test.logger.error('Failure to read acclerations in range %g <= a <= %g'
            % (accel_mag_min, accel_mag_max))
        return stf.FAIL
    
    # Update measurements using median sample
    for ix in range( len(mags) ):
        if mags[ix] == median:
            inclination = math.degrees(math.acos(samples[ix][2] / median) )
            test.measurements.accel_mag = median
            test.measurements.inclination = inclination
            test.logger.info('Successfully read %d samples in %g s' %
                (len(mags), time.time() - time_start ) )
            return  # successful reads return point

    test.logger.error('Unable to find measurement for mag %g' % (median))
    return stf.FAIL


stf.register(
    # version should change if your code changes (required if this test has
    # been used in production). You're in charge of this version as a test writer
    version='1.0',

    run=run_test,

    # optional: test name is generated from filename if not provided
    test_name=Me,
    # optional: test_desc is a description of your test which will appear in the output
    test_desc='Test acceleration magnitude measured by Accelerometer Sensor ADXL355',
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
