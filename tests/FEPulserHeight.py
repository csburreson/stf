import stf
import time
import numpy as np

@stf.measures(stf.M('feph').in_range('{exp_x}', '{exp_y}'))
def run_test(test, session, channel, dac_val,
             dac_val_fepulser, nsamples=128, **kw):
    if nsamples < 16 or nsamples % 4 != 0:
        test.logger.error('Number of samples must be at least 16 and divisible by 4')
        return stf.FAIL

    session.setDEggConstReadout(channel, 1, nsamples)

    # measure baseline
    dac_channel_dict = {0:'A', 1:'B'}
    session.setDAC(dac_channel_dict[channel], dac_val)
    time.sleep(0.1)
    session.testDEggCPUTrig(channel)
    readout = session.testDEggWaveformReadout()
    baseline = np.mean(readout['waveform'])
    
    test.logger.info('Enabling FEPulser for channel {}'.format(channel))
    session.enableFEPulser(channel,2)
    session.setDAC('D', dac_val_fepulser)
    time.sleep(0.1)

    thres = baseline+20
    session.testDEggThresholdTrig(channel, int(thres))
    readout = session.testDEggWaveformReadout()
    wf = np.asarray(readout["waveform"])-baseline
    # see tests/template.json for testconfig
    test.measurements.feph = wf.max()

    test.logger.info(f'Baseline from channel {channel}: {baseline}')
    test.logger.info(f'Trigger threshold: {thres}')
    test.logger.info(f'FEPulser height over baseline: {test.measurements.feph}')


stf.register(
    # version should change if your code changes (required if this test has
    # been used in production). You're in charge of this version as a test writer
    version='1.0',

    # run is required and points to the test function intended to be run
    run=run_test,

    ##########

    # optional: test name is generated from filename if not provided
    test_name='FEPulserHeight',
    # optional: test_desc is a description of your test which will appear in the output
    test_desc='Inject pulses into FE at a high DAC setting, measure height',
    # optional: defaults to std.testclasses.MainboardTest
    test_class=stf.testclasses.MainboardTest,
    # override: use 'config_file' to point to a different location for config
    #   (default is STF_HOME/data/testconfig/<test_name>.json )
    # (if not provided, the framework would try to open "foo.json" with this definition)
    # config_file=None
)

# use "python <this-file.py>" to run
if __name__ == '__main__':
    stf.run()
