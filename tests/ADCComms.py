# Aaron Fienberg
#
# Tests communcation with an ADS4149 chip

import stf
from iceboot.ads4149 import setRegister as setADCRegister
from iceboot.ads4149 import ADS_4149_CUSTOM_PATTERN_HIGH_REG
from iceboot.ads4149 import ADS_4149_CUSTOM_PATTERN_LOW_REG

PATTERNS = [0x2aaa, 0x1555]
MEASUREMENT_NAMES = ['first_read', 'second_read']


@stf.measures(stf.M(MEASUREMENT_NAMES[0]).equals(PATTERNS[0]),
              stf.M(MEASUREMENT_NAMES[1]).equals(PATTERNS[1]))
def run_test(test, session, channel):
    ''' Writes and reads back test patterns to the
    ADS4149 custom pattern registers '''

    for pattern, measurement_name in zip(PATTERNS, MEASUREMENT_NAMES):
        read_val = write_custom_pattern(session, channel, pattern)
        setattr(test.measurements, measurement_name, read_val)


stf.register(
    version='1.0',
    test_name='ADCComms',
    run=run_test,
)


def write_custom_pattern(session, channel, pattern):
    ''' writes <pattern> to the ADS4149 custom pattern
    registers and then reads the custom pattern back.

    returns the value that was read from the chip '''

    setADCRegister(session, ADS_4149_CUSTOM_PATTERN_LOW_REG, pattern, channel)

    low = session.readADS4149(
        channel, ADS_4149_CUSTOM_PATTERN_LOW_REG["address"])
    high = session.readADS4149(
        channel, ADS_4149_CUSTOM_PATTERN_HIGH_REG["address"])

    return (high << 6) | (low >> 2)


if __name__ == '__main__':
    stf.run()
