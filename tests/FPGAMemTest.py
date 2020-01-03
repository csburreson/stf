# Jim Braun
#
# Read an FPGA register and compare it to an expected value.
# This is primarily to report the result of the FPGA memory check.
#

import stf


@stf.measures(stf.M('memtestValue').equals(True))
def run_test(test, session, register):
    test.measurements.memtestValue = session.memtest()


stf.register(
    version='1.0',
    test_name='FPGAMemTest',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()