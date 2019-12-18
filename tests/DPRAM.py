# Jim Braun
#
# Test that we can read/write the FPGA DPRAM
#

import stf

# DPRAM is 4kB, or 2 kwords, or 1k 2-word patterns
TEST_PATTERNS = [[0x5555, 0xAAAA] * 1024,
                 [0xAAAA, 0x5555] * 1024]


@stf.measures(stf.M('DPRAMIOSuccess').equals(True))
def run_test(test, session):
    
    test.measurements.DPRAMIOSuccess = False
    
    for pattern in TEST_PATTERNS:
        session.fpgaWrite(addr, pattern)
        if session.fpgaRead(addr, len(pattern)) != pattern:
            return

    test.measurements.DPRAMIOSuccess = True


stf.register(
    version='1.0',
    test_name='DPRAM',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
