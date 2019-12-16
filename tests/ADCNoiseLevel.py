# Aaron Fienberg
#
# Creates an ADC noise histogram
# records the full histogram and the RMS
#

import stf
import time
from iceboot.ads4149 import setRegister as setADCRegister
from iceboot.ads4149 import ADS_4149_HP1_REG, ADS_4149_HP2_REG
from DEggTest.adc_histogram import *
from DEggTest.fpga_reg import fpga_write


@stf.measures(stf.M('noise_histogram'),
              stf.M('noise_std').in_range('{noise_min}', '{noise_max}',
                                          type=float))
def run_test(test, session, channel, dac_val,
             wfm_period=3, wfm_len=1000, n_waveforms=1000, **kwargs):
    ''' acquires an ADC noise histogram '''
    configure_mainboard(session, channel, dac_val, wfm_len)

    adc_hist = make_sw_trig_histogram(session, channel,
                                      wfm_period, n_waveforms)

    test.measurements.noise_histogram = adc_hist

    noise_std = hist_std(adc_hist)
    test.logger.info(f'Noise level from channel {channel}: '
                     f'{noise_std}')
    test.measurements.noise_std = noise_std


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


if __name__ == '__main__':
    stf.run()
