import stf
from DEggTest.fepulser import get_pulser_charge
import numpy as np

@stf.measures(stf.M('r2').expectRange('{exp_x}', '{exp_y}', type=float))
def run_test(test, session, channel, dac_val, dac_val_fepulser_start,
             dac_val_fepulser_step, dac_val_fepulser_nstep, bins_before_peak, bins_after_peak,
             nsamples=128, n_waveforms=10, **kw):
    if nsamples < 16 or nsamples % 4 != 0:
        test.logger.error('Number of samples must be at least 16 and divisible by 4')
        return stf.FAIL

    qs = []
    dac_vals = []
    for i in range(dac_val_fepulser_nstep+1):
        _ = dac_val_fepulser_start+i*dac_val_fepulser_step
        qs_dac = [get_pulser_charge(
            session, channel, nsamples, dac_val, _,
            bins_before_peak, bins_after_peak) for _i in range(n_waveforms)]
        test.logger.info(qs_dac)
        qs.append(sum(qs_dac)/len(qs_dac))
        dac_vals.append(_)
        stf.debug('abc {}: {}'.format(_, sum(qs_dac)/len(qs_dac)))

    qs = np.asarray(qs)
    dac_vals = np.asarray(dac_vals)
    slope, intercept = np.polyfit(dac_vals, qs, 1)
    
    # see tests/template.json for testconfig
    test.measurements.r2 = 1-np.sum((qs-slope*dac_vals-intercept)**2)/np.sum((qs-qs.mean())**2)

    test.logger.info(f'FEPulser slope: {slope}')
    test.logger.info(f'FEPulser intercept: {intercept}')
    test.logger.info(f'FEPulser R2: {test.measurements.r2}')


stf.register(
    # version should change if your code changes (required if this test has
    # been used in production). You're in charge of this version as a test writer
    version='1.0',

    # run is required and points to the test function intended to be run
    run=run_test,

    ##########
    # optional: test_desc is a description of your test which will appear in the output
    test_desc='Inject pulses into FE pulser, measure charge linearity vs DAC setting',
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
