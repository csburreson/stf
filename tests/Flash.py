# Jim Braun
#
# Tests that MCU can write/read SPI flash chip
#

import stf
import os


FLASH_STR = "FLASH_TEST_STRING"


@stf.measures(stf.M('flashIOSuccess').equalsParam('flashIOSuccessValue', type=bool))
def run_test(test, session, testFileName):
    test.measurements.flashIOSuccess = False
    
    if os.path.exists(testFileName):
        test.logger.info("Test file %s: exists" % testFileName)
        return

    try:
        with open(testFileName, "wb") as f:
            f.write(FLASH_STR)
    except:
        test.logger.info("Unable to write test file %s" % testFileName)
        return
    
    try:
        test.measurements.flashIOSuccess = perform_test(session, testFileName)
    except Exception as e:
        raise e
    finally:
        os.remove(testFileName)


def perform_test(session, testFileName):

    fileEntries = [x for x in session.flashLS() if x["Name"] == testFileName]
    if len(fileEntries) != 0:
        return False

    session.ymodemFlashUpload(testFileName, testFileName)
    fileEntries = [x for x in session.flashLS() if x["Name"] == testFileName]
    if len(fileEntries) == 0:
        return False
    
    if int(fileEntries[0]["Size"]) != len(FLASH_STR):
        session.flashRemove(testFileName)
        return False
    
    if session.flashCat(testFileName) != FLASH_STR:
        session.flashRemove(testFileName)
        return False

    session.flashRemove(testFileName)
    
    fileEntries = [x for x in session.flashLS() if x["Name"] == testFileName]
    if len(fileEntries) != 0:
        return False
    
    return True


stf.register(
    version='1.0',
    test_name='Flash',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
