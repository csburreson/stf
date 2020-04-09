# Aaron Fienberg
#
# Scans through DAC values and and measures ADC mean and noise vs DAC setting
#

import stf
import time
from iceboot.ads4149 import setRegister as setADCRegister
from iceboot.ads4149 import ADS_4149_HP1_REG, ADS_4149_HP2_REG
from DEggTest.adc_histogram import *
from DEggTest.fpga_reg import fpga_write


@stf.measures(stf.M('dac_scan_results'),
              stf.M('fit_Rsq').expectRange(
                  '{Rsq_min}', '{Rsq_max}', type=float),
              stf.M('fit_y_intercept'),
              stf.M('fit_x_intercept').expectRange(
                  '{intercept_min}', '{intercept_max}', type=float),
              stf.M('fit_slope').expectRange('{slope_min}', '{slope_max}',
                                             type=float))
def run_test(test, session, channel, n_settings,
             adc_fit_range_min, adc_fit_range_max,
             wfm_period=3, wfm_len=1000, wfms_per_setting=10):
    scan_results = do_dac_scan(session, channel, wfm_period,
                               wfm_len, n_settings, wfms_per_setting)

    fit_res, Rsq = line_fit(scan_results, adc_fit_range_min, adc_fit_range_max)
    slope = fit_res[0]
    y_int = fit_res[1]
    x_int = -y_int/slope

    test.logger.info(f'R^2: {Rsq:.6f}')
    test.logger.info(f'Measured slope: {slope} ADU / DAC setting')
    test.logger.info(f'Measured x-intercept: {x_int:.0f}')

    test.measurements.dac_scan_results = scan_results
    test.measurements.fit_Rsq = Rsq
    test.measurements.fit_y_intercept = y_int
    test.measurements.fit_x_intercept = x_int
    test.measurements.fit_slope = slope


stf.register(
    version='1.0',
    test_name='DACScan',
    run=run_test,
)


def configure_mainboard(session, channel, wfm_len):
    # set the high performance mode registers
    for reg in [ADS_4149_HP1_REG, ADS_4149_HP2_REG]:
        setADCRegister(session, reg, 'BestPerformance', channel)

    # set the wfm len
    fpga_write(session, f'test_conf[{channel}]', int(wfm_len//4))


def line_fit(scan_res, adc_fit_range_min, adc_fit_range_max):
    ''' returns (polyfit result, r^2)'''

    settings = np.array(scan_res['dac_settings'])
    mins = np.array(scan_res['mins'])
    maxs = np.array(scan_res['maxs'])
    means = np.array(scan_res['means'])

    # do not include saturating/clipping settings in the fit
    fit_inds = np.logical_and(mins > adc_fit_range_min,
                              maxs < adc_fit_range_max)

    pfit_res = np.polyfit(settings[fit_inds], means[fit_inds], 1)

    # calculate r^2 from fit result
    y_vals = means[fit_inds]
    y_mean = np.average(y_vals)
    SStot = np.sum((y_vals-y_mean)**2)

    predicted = np.poly1d(pfit_res)(settings[fit_inds])
    SSres = np.sum((y_vals-predicted)**2)

    Rsq = 1 - SSres/SStot

    return pfit_res, Rsq


def do_dac_scan(session, channel, wfm_period=3, wfm_len=1000,
                n_settings=100, wfms_per_setting=10):
    ''' returns a dictionary containing the dac scan results '''

    configure_mainboard(session, channel, wfm_len)

    # convert digitizer channel to DAC channel
    dac_chan = chr(ord('A') + channel)

    dac_settings = np.uint16(np.linspace(0, 0xffff, n_settings))

    mins = []
    maxs = []
    means = []
    modes = []
    stds = []

    for dac_setting in dac_settings:
        session.setDAC(dac_chan, dac_setting)
        time.sleep(0.1)

        hist = make_sw_trig_histogram(session, channel,
                                      wfm_period, wfms_per_setting)

        # record histogram statistics
        mins.append(hist['min'])
        maxs.append(hist['max'])
        means.append(hist_mean(hist))
        modes.append(np.argmax(hist['counts']) + mins[-1])
        stds.append(hist_std(hist))

    # convert dac_settings to a python list for uniformity
    return {'dac_settings': list(dac_settings),
            'mins': mins, 'maxs': maxs,
            'means': means, 'modes': modes, 'stds': stds}


if __name__ == '__main__':
    stf.run()
