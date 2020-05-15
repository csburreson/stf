# The purpose of this test is to verify the the DEgg mainboard HV interfaces,
# using a test-only loopback cable, instead of an HV board.  The loopback cable
# sends the channel DAC setpoint output voltage back to the corresponding
# SLO_ADC HV monitor input. The emulated HV "value" is then read from the
# SLO_ADC. The HV board should not be installed. Note that DAC setpoint voltage
# outputs vary from 0-5V, and SLO_ADC inputs vary from 0-1V, so read value
# scaling must be adjusted, and the max SLO_ADC input must be limited, via
# DAC_PRESET_HW_LIMIT.  All engineering units are Volts.

import stf
import time

HV_STABILIZATION_DELAY = 0.2

# For HV loopback cable, limit input to SLO_ADC to be less than 1V max input.
DAC_PRESET_HW_LIMIT = 400.0

@stf.measures(stf.M('HVmonV').expectRange('{HVmin}','{HVmax}',type=float))
def run_test(test, session, channel, dacPreset):
    # Validate inputs
    if (channel < 0 or channel > 1):
        raise stf.STFException('invalid channel %d' % (channel))
    if (dacPreset < 0 or dacPreset > DAC_PRESET_HW_LIMIT):
        raise stf.STFException('invalid dacPreset %f' % (dacPreset))

    # Configure HV.
    session.setDEggHV(channel, dacPreset)
    session.enableHV(channel)
    time.sleep(HV_STABILIZATION_DELAY)

    # Read HV supply per-channel voltage monitors, EU = Volts.
    sloAdcChannel = 8 + channel * 2
    test.measurements.HVMonV = session.sloAdcReadChannel(sloAdcChannel)

    # Disable HV.
    session.disableHV(ch)

stf.register(
    version = '1.0',
    run = run_test
)

# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
