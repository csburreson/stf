# Aaron Fienberg
#
# Creates an ADC noise histogram
# records the full histogram and some summary statistics
#
# Quantiles are reported relative to the ADC mode

import stf
import time
from iceboot.ads4149 import setRegister as setADCRegister
from iceboot.ads4149 import ADS_4149_HP1_REG, ADS_4149_HP2_REG
from DEggTest.adc_histogram import *
from DEggTest.fpga_reg import fpga_write


@stf.measures(stf.M('noise_histogram'),
              stf.M('adc_mean'),
              stf.M('adc_mode'),
              stf.M('one_pct_quantile').expectRange(
                  '{one_pct_min}', '{one_pct_max}', type=int),
              stf.M('ninetynine_pct_quantile').expectRange(
                  '{ninetynine_pct_min}', '{ninetynine_pct_max}', type=int),
              stf.M('noise_std').expectRange('{noise_min}', '{noise_max}',
                                             type=float))
def run_test(test, session, channel, dac_val,
             wfm_period=3, wfm_len=1000, n_waveforms=1000):
    ''' acquires an ADC noise histogram '''
    configure_mainboard(session, channel, dac_val, wfm_len)

    adc_hist = make_sw_trig_histogram(session, channel,
                                      wfm_period, n_waveforms)

    adc_mean = hist_mean(adc_hist)
    adc_mode = np.argmax(adc_hist['counts']) + adc_hist['min']
    noise_std = hist_std(adc_hist)
    one_pct_q, ninetynine_pct_q = calculate_quantiles(adc_hist)

    test.logger.info(f'Baseline from channel {channel}: '
                     f'{adc_mean}')
    test.logger.info(f'ADC mode: '
                     f'{adc_mode}')
    test.logger.info(f'Noise level: {noise_std}')
    test.logger.info(f'low extreme: {adc_hist["min"]}')
    test.logger.info(f'1% quantile: {one_pct_q}')
    test.logger.info(f'high extreme: {adc_hist["max"]}')
    test.logger.info(f'99% quantile: {ninetynine_pct_q}')

    test.measurements.noise_histogram = adc_hist
    test.measurements.adc_mean = adc_mean
    test.measurements.adc_mode = adc_mode
    test.measurements.noise_std = noise_std
    test.measurements.one_pct_quantile = one_pct_q - adc_mode
    test.measurements.ninetynine_pct_quantile = ninetynine_pct_q - adc_mode


stf.register(
    version='1.0',
    test_name='ADCNoiseLevel',
    run=run_test,
)


def configure_mainboard(session, channel, dac_val, wfm_len):
    # set the high performance mode registers
    for reg in [ADS_4149_HP1_REG, ADS_4149_HP2_REG]:
        setADCRegister(session, reg, 'BestPerformance', channel)

    if dac_val is not None:
        # convert digitizer channel to DAC channel
        dac_chan = chr(ord('A') + channel)
        session.setDAC(dac_chan, dac_val)
        time.sleep(0.1)

    # set the wfm len
    fpga_write(session, f'test_conf[{channel}]', int(wfm_len//4))


def calculate_quantiles(hist):
    ''' calculates the one percent and 99 percent quantiles '''
    cdf = np.cumsum(hist['counts'])/np.sum(hist['counts'])

    # smallest x where p(ADC <= x) >= 0.01
    one_pct_q = hist['min'] + np.argwhere(cdf >= 0.01)[0][0]

    # smallest x where p(ADC <= x) >= 0.99
    ninetynine_pct_q = hist['min'] + np.argwhere(cdf >= 0.99)[0][0]

    return one_pct_q, ninetynine_pct_q


if __name__ == '__main__':
    stf.run()
