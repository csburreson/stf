# Ken'ichi KIN
#
# Tests communication with camera

import stf
import time

TEST_REGISTER = 55 #0x55

@stf.measures(stf.M('RegisterValue1').equalsParam('ExpectedRegisterValue'),
              stf.M('RegisterValue2').equalsParam('ExpectedRegisterValue'),
              stf.M('RegisterValue3').equalsParam('ExpectedRegisterValue'))
def run_test(test, session):

    session.enableCalibrationPower()
    session.setCalibrationSlavePowerMask(1)
    session.setCameraEnableMask(0x15)
    for cam in range(1,4):
        time.sleep(0.2) #increase sleep time if you fail to run this test
        session.writeCameraRegister(cam, TEST_REGISTER, 0)
        readRegister(test, session, cam)

        
stf.register(
    version='1.0',
    test_name='CameraComms',
    run=run_test,
)


def readRegister(test, session, cam):
    # Read register value for each camera
    if cam == 1:
        test.measurements.RegisterValue1 = hex(session.readCameraRegister(1, 0))
    elif cam == 2:
        test.measurements.RegisterValue2 = hex(session.readCameraRegister(2, 0))
    elif cam == 3:
        test.measurements.RegisterValue3 = hex(session.readCameraRegister(3, 0))
        

# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
