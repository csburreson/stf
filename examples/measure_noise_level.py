import teflon
import numpy as np

### made up fns run this "example"
def parseTestWaveform(x, channel):
    return {'channel': channel, 'waveform': []}

def fpga_write(*args):
    pass

@teflon.measures(teflon.Measurement('noise'))
def measure_noise_level(test, session, channel=None, n_waveforms=None):
    #session.startDEggSWTrigStream(channel, 5)

    var_sum = 0
    n_samps = 0

    for i in range(n_waveforms):
        wfm = parseTestWaveform(session, channel)

        if wfm['channel'] != channel:
            raise RuntimeError('Read a waveform from the wrong channel!')

        samples = wfm['waveform']
        n_samps += len(samples)
        var_sum += len(samples)*(np.std(wfm['waveform'])**2)

    #session.endStream()
    test.measurements.noise = np.sqrt(var_sum/n_samps)

    if test.measurements.noise is np.nan:
        return teflon.STOP

    if test.measurements.noise == 42:
        # fail test, but continue
        return teflon.FAIL

    return teflon.CONTINUE


@teflon.test
def setup(test, session):
    fpga_write(session, 'wvb_reader_enable', 1)
    fpga_write(session, 'dpram_select', 4)


@teflon.register(version='1.0', config_file='data/testconfig/measure_noise_level.json')
class MeasureNoiseLevel(teflon.MainboardTest):
    '''measure the noise level'''
    TESTS = [
        setup,
        # can call test like this, which makes channel the 3rd arg (first kwarg)
        measure_noise_level.with_args(channel=0),
        measure_noise_level.with_args(channel=1),
    ]
    

if __name__ == '__main__':
    teflon.run()
