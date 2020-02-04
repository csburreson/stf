# Ryo Nagai / Ken'ichi Kin
#
# Supply 200V to ch0/ch1 -> Check readback values

import stf
import time

@stf.measures(stf.M('DEggHVSupply0').expectRange('{expected_degghvsupply_min}','{expected_degghvsupply_max}',type=float),
              stf.M('DEggCurrent0').expectRange('{expected_deggcurrent_min}','{expected_deggcurrent_max}',type=float),
              stf.M('DEggHVSupply1').expectRange('{expected_degghvsupply_min}','{expected_degghvsupply_max}',type=float),
              stf.M('DEggCurrent1').expectRange('{expected_deggcurrent_min}','{expected_deggcurrent_max}',type=float))

def run_test(test, session):
    '''this test checks the applied HV voltage is correct'''
    #CH0
    readVal(test,session,0)
    #CH1
    readVal(test,session,1)

stf.register(
    version='1.0',
    test_name='DEggHVSupply',
    run=run_test,
)

def readVal(test, session, ch):
    session.setDEggHV(ch, 200)
    session.enableHV(ch)
    time.sleep(0.2)
    observed_hvvalue = session.sloAdcReadChannel(8+ch*2)
    time.sleep(0.2)
    observed_current = session.sloAdcReadChannel(9+ch*2)
    if ch == 0:
        test.logger.info('Measured HV value for ch0: {}'.format(observed_hvvalue))
        test.measurements.DEggHVSupply0 = observed_hvvalue
        test.logger.info('Measured Current value for ch0: {}'.format(observed_current))
        test.measurements.DEggCurrent0 = observed_current
    else:
        test.logger.info('Measured HV value for ch1: {}'.format(observed_hvvalue))
        test.measurements.DEggHVSupply1 = observed_hvvalue
        test.logger.info('Measured Current value for ch1: {}'.format(observed_current))
        test.measurements.DEggCurrent1 = observed_current
    session.disableHV(ch)


# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
