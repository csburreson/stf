# Jim Braun
#
# Read an FPGA register and compare it to an expected value.
# This is primarily to report the result of the FPGA memory check.
#

import stf


@stf.measures(stf.M('registerValue').equalsParam('expectedRegisterValue', type=int))
def run_test(test, session, register):
    test.measurements.registerValue = int(session.fpgaRead(register, 1)[0])


stf.register(
    version='1.0',
    test_name='FPGARegisterValueCheck',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()