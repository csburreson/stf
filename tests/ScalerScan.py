# Jim Braun
#
#

import stf
import os
import time

# Measure the rate of ADC counts at some level above baseline
@stf.measures(stf.M('trigger_rate'),
              stf.M('rate').expectRange(0, '{maxRate}', type=int))
def run_test(test, session, channel, biasDACValue,
             integrationTimeUS, dacIncrement, histogramBins):
    
    # Get a baseline
    session.setDAC('A', biasDACValue)
    session.setDAC('B', biasDACValue)
    session.setDEggConstReadout(channel, 1, 256)
    
    time.sleep(0.3)
    session.testDEggCPUTrig(channel)
    readout = session.testDEggWaveformReadout()
    if readout is None or len(readout["waveform"]) == 0:
        raise stf.STFException("Unable to acquire a CPU trigger")
    baseline = int(sum(x for x in readout["waveform"]) / 
                                    len(readout["waveform"]))

    if baseline == 0:
        raise stf.STFException("Baseline is zero")

    session.enableScalers(channel, integrationTimeUS, 240) # 1 us deadtime
    session.enableDEggTrigger(channel)
    adc = baseline + dacIncrement
    if adc > 16383:
        raise stf.STFException("Threshold is above max ADC range")
    session.setDEggTriggerConditions(channel, adc)
    integrationTime = 1e-6 * integrationTimeUS
    time.sleep(integrationTime * 2.2)
    count = session.getScalerCount(channel)
    rate =  float(count) / integrationTime
    if rate is None:
        raise stf.STFException('scalar rate calculation error')

    test.measurements.rate =  rate

    integrationTimeUS *= 0.1
    integrationTime = 1e-6 * integrationTimeUS
    session.enableScalers(channel, integrationTimeUS, 240) # 1 us deadtime
    rates = []
    adcValues = []
    for i in range(histogramBins):
        adc = baseline + i
        if adc > 16383:
            raise stf.STFException("Threshold is above max ADC range")
        session.setDEggTriggerConditions(channel, adc)
        time.sleep(integrationTime * 2.2)
        adcValues.append(i)
        rates.append(float(session.getScalerCount(channel)) / integrationTime)

    test.measurements.trigger_rate = {"ADC (count above baseline)": adcValues,
                                      "Rate (Hz)": rates}


stf.register(
    version='1.0',
    test_name='ScalerScan',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
