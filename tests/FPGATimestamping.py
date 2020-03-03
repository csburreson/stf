# Aaron Fienberg
#
# Compares FPGA timestamps to the CPU clock
#

import stf
import time
from DEggTest.fpga_reg import fpga_write
from iceboot.test_waveform import parseTestWaveform
import numpy as np


@stf.measures(stf.M('domclock_diff').expectRange('{clockdiff_min}',
                                                 '{clockdiff_max}',
                                                 type=float),
              stf.M('period_diff').expectRange('{perioddiff_min}',
                                               '{perioddiff_max}',
                                               type=float))
def run_test(test, session, channel,
             wfm_period=2, wfm_len=32, n_waveforms=1000,
             domclock_freq=60e3, wfmclock_freq=240e3):
    ''' sends periodic software triggers and compares the
    waveform timestamps to the cpu clock 

    parameter frequencies are in units of kHz
    periods are in units of ms
    '''
    fpga_write(session, f'test_conf[{channel}]', int(wfm_len//4))

    last_tick = session.domClock()
    start_time = last_tick / domclock_freq

    cpu_times = []
    fpga_times = []

    session.startDEggSWTrigStream(channel, wfm_period)
    for _ in range(n_waveforms):
        wfm = parseTestWaveform(session.readWFMFromStream())

        if wfm['channel'] != channel:
            raise RuntimeError('Read a waveform from the wrong channel!')

        cpu_times.append(time.time())

        this_tick = wfm['timestamp']
        # check for clock rollover
        if this_tick < last_tick:
            this_tick += (1 << 48)
        fpga_times.append(this_tick/wfmclock_freq)

        lsat_tick = this_tick

    session.endStream()

    # convert to ms
    cpu_times = np.array(cpu_times) * 1000

    fpga_times = np.array(fpga_times)

    # do not include the first readout in the period measurement
    cpu_period = np.average(cpu_times[2:] - cpu_times[1:-1])
    fpga_period = np.average(fpga_times[2:] - fpga_times[1:-1])

    timestamp_diff = fpga_times[0] - start_time

    period_diff = fpga_period - cpu_period

    test.logger.info('timestamp - DOM clock: '
                     f'{(fpga_times[0] - start_time)*1000} us')
    test.logger.info(f'CPU period: {cpu_period}')
    test.logger.info(f'FPGA period: {fpga_period}')
    test.logger.info(f'Period diff: {(fpga_period - cpu_period)*1000} us')

    test.measurements.domclock_diff = timestamp_diff
    test.measurements.period_diff = period_diff


stf.register(
    version='1.0',
    test_name='FPGATimestamping',
    run=run_test,
)

if __name__ == '__main__':
    stf.run()
