# Jim Braun
#
# Tests that interlocks have the expected values
#

import stf
import os


# DPRAM is 4kB or 2 kwords, or 1k 2-word patterns
CNT = 16
WCNT = 2 * CNT
TEST_PATTERNS = [[0x5555, 0xAAAA] * CNT,
                 [0xAAAA, 0x5555] * CNT]


@stf.measures(stf.M('DPRAMIOSuccess').equals(True))
def run_test(test, session):
    
    test.measurements.DPRAMIOSuccess = False
    
    for pattern in TEST_PATTERNS:
        for addr in range(0, 2048, WCNT):
            session.fpgaWrite(addr, pattern)
        for addr in range(0, 2048, WCNT):
            if session.fpgaRead(addr, WCNT) != pattern:
                return

    test.measurements.DPRAMIOSuccess = True


stf.register(
    version='1.0',
    test_name='DPRAM',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
