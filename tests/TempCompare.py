# Ken'ichi Kin
#
# Compare temperature value readout from Accelerometer/Magnetometer/Pressuresensor to that readout from SLO_ADC

import stf
import time

@stf.measures(stf.M('TempDiffAcc').expectRange('{expected_diffacc_min}','{expected_diffacc_max}',type=float),
              stf.M('TempDiffMag').expectRange('{expected_diffmag_min}','{expected_diffmag_max}',type=float),
              stf.M('TempDiffPres').expectRange('{expected_diffpres_min}','{expected_diffpres_max}',type=float))

def run_test(test, session):
    ''' Accelerometer '''
    TempSLOADC = session.sloAdcReadChannel(7)
    diffAcc = session.readAccelerometerTemperature() - TempSLOADC
    test.measurements.TempDiffAcc = diffAcc
    test.logger.info('Temperature difference for Accelerometer: {}'.format(diffAcc))

    ''' Magnetometer '''
    TempSLOADC = session.sloAdcReadChannel(7)
    diffMag = session.readMagnetometerTemperature() - TempSLOADC
    test.measurements.TempDiffMag = diffMag
    test.logger.info('Temperature difference for Magnetometer: {}'.format(diffMag))

    ''' Pressuresensor '''
    TempSLOADC = session.sloAdcReadChannel(7)
    diffPres = session.readPressureSensorTemperature() - TempSLOADC
    test.measurements.TempDiffPres = diffPres
    test.logger.info('Temperature difference for Pressuresensor: {}'.format(diffPres))
    
stf.register(
    version='1.0',
    test_name='TempCompare',
    run=run_test,
)

# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
