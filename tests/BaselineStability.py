import stf
import time
import numpy as np
from iceboot.test_waveform import parseTestWaveform


@stf.measures(stf.M('reducedChi2').expectRange('{exp_x}', '{exp_y}', type=float))
def run_test(test, session, channel, dac_val,
             nsamples=2048, trig_delay=2, interval=60, **kw):
    if nsamples < 16 or nsamples % 4 != 0:
        test.logger.error('Number of samples must be at least 16 and divisible by 4')
        return stf.FAIL

    session.setDEggConstReadout(int(channel), 1, nsamples)

    # sample baseline mean and rms for 60 s
    session.startDEggSWTrigStream(int(channel), 
                                  int(trig_delay))
    start = time.time()
    means = []
    rmss = []
    # skip first readout
    parseTestWaveform(session.readWFMFromStream())
    
    readout = parseTestWaveform(session.readWFMFromStream())
    wf = readout['waveform']
    mean = np.mean(wf)
    rms = np.std(wf)

    chi2 = 0
    ndof = 0
    while time.time() - start < interval:
        try:
            readout = parseTestWaveform(session.readWFMFromStream())
        except IOError:
            print('Timeout! Ending waveform stream and exiting')
            session.endStream()
            break

        # Check for timeout
        if readout is None:
            continue
        wf = np.asarray(readout["waveform"])
        # Fix for 0x6a firmware
        if len(wf) != nsamples:
            continue

        chi2 += np.sum((wf - mean)**2/rms**2)
        ndof += len(wf)

    session.endStream()
    stf.debug(f'chi2 {chi2}')
    stf.debug(f'ndof {ndof}')
    stf.debug(f'chi2/ndof {chi2/ndof}')
    test.measurements.reducedChi2 = chi2/ndof

    test.logger.info(f'Baseline Chi2/NDOF: {test.measurements.reducedChi2}')


stf.register(
    # version should change if your code changes (required if this test has
    # been used in production). You're in charge of this version as a test writer
    version='1.0',

    # run is required and points to the test function intended to be run
    run=run_test,

    ##########

    # optional: test_desc is a description of your test which will appear in the output
    test_desc='Test baseline stability over 60 s',
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
