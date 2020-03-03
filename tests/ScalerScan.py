# Jim Braun
#
# Tests that interlocks have the expected values
#

import stf
import os
import time

# Measure the rate of ADC counts at some level above baseline
@stf.measures(stf.M('rate').expectRange(0, '{maxRate}', type=int))
def run_test(test, session, channel, biasDACValue,
             integrationTimeUS, dacIncrement):
    
    # Get a baseline
    session.setDAC('A', biasDACValue)
    session.setDAC('B', biasDACValue)
    session.setDEggConstReadout(channel, 1, 256)
    
    time.sleep(0.3)
    session.testDEggCPUTrig(channel)
    readout = session.testDEggWaveformReadout()
    if readout is None or len(readout["waveform"]) == 0:
        raise Exception("Unable to acquire a CPU trigger")
    baseline = int(sum(x for x in readout["waveform"]) / 
                                    len(readout["waveform"]))

    if baseline == 0:
        raise Exception("Baseline is zero")

    session.enableScalers(channel, integrationTimeUS, 240) # 1 us deadtime
    session.enableDEggTrigger(channel)
    adc = baseline + dacIncrement
    if adc > 16383:
        raise Exception("Threshold is above max ADC range")
    session.setDEggTriggerConditions(channel, adc)
    integrationTime = 1e-6 * integrationTimeUS
    time.sleep(integrationTime * 2.2)
    count = session.getScalerCount(channel)
    test.measurements.rate =  float(count) / integrationTime


stf.register(
    version='1.0',
    test_name='ScalerScan',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
