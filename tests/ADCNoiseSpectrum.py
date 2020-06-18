# Save, validate ADC noise spectrum
# Shamelessly plagiarized from STM32Tools python/DEggTest/adcFFT.py
# by J. Weber

import stf
import time
import numpy as np

TEST = 'ADCNoiseSpectrum'
MIN_SAMPLES = 16
MAX_CHANNEL = 1
DIGITIZER_FREQ = 240000000
DAC_SET_DELAY_SEC = 0.1
MAX_DAC_VAL = 0xffff

# Convert DAC signed int16 to int
def int16toInt(int16):
    Int = []
    for i16 in int16:
        Int.append(((i16 + 0x8000) & 0xffff) - 0x8000)
    return Int

@stf.measures(
    stf.M('noise_spectrum'),
    stf.M('timeDomain'),
    stf.M('max_noise_power').expectRange(
        '{noise_power_min}', '{noise_power_max}', type=float))
def run_test(test, session, channel, scanCount, scanSamples,
    dac_val, nWaveFormBins, plot=False):

    # Validate input arguments
    nSamples = int(scanSamples / 4) * 4
    if nSamples != scanSamples:
        test.logger.warning('scanSamples %d not divisible by 4, using %d' %
        (scanSamples,nSamples))
    if (nSamples < MIN_SAMPLES):
        raise stf.STFException('scanSamples %d must be at least %d' %
            (nSamples, MIN_SAMPLES))
    if (channel < 0 or channel > MAX_CHANNEL):
        raise stf.STFException('bad channel %d' % (channel))
    if (dac_val < 0 or dac_val > MAX_DAC_VAL):
        raise stf.STFException('bad dac_val %d' % (dac_val))
    if (nWaveFormBins is None):
        raise stf.STFException('bad nWaveFormBins value')

    # convert digitizer channel to DAC channel 'A' - 'H'
    dac_chan = chr(ord('A') + channel)
    session.setDAC(dac_chan, dac_val)
    time.sleep(DAC_SET_DELAY_SEC)

    session.setDEggConstReadout(channel, 1, nSamples)

    # Build output power spectrum array
    output = []
    for _ in range(int(scanCount)):
        # Trigger a scan and readout waveform
        session.testDEggCPUTrig(channel)
        readout = session.testDEggWaveformReadout()
        if readout is None:
            continue
        # Readout waveform. Units: LSBs
        wf = readout["waveform"]
        if len(output) == 0:
            output = [0.] * len(wf)
        else:
            if len(wf) != len(output):
                continue
        av = (float(sum(wf))) / len(wf)
        for i in range(len(wf)):
            wf[i] -= av
        # Calculate power density spectrum. Units: (LSB)**2.
        # Note: fft() returns complex vectors, abs() returns the magnitude.
        ps = np.abs(np.fft.fft(wf))**2
        for i in range(len(ps)):
            output[i] += ps[i]

    sample = np.arange(0, nWaveFormBins)
    scanI16 = readout["waveform"][:nWaveFormBins]
    scan = { 'sample': sample, 'LSB': int16toInt(scanI16)}
    test.measurements.timeDomain = scan

    # Development use
    if plot:
        import matplotlib.pyplot as plt
        plt.xlabel("sample")
        plt.ylabel("LSB")
        title = '%s-chan%d-dac%d-bins%d-wf' % (TEST, channel, dac_val, nWaveFormBins)
        plt.title(title)
        plt.plot(scan['sample'], scan['LSB'] )
        plt.savefig(title)
        plt.clf()

    # Normalize output over scanCount and samples, enabling the same pass/fail
    # criteria to be used over different scanCount, scanSamples args.
    for i in range(len(output)):
        output[i] /= (scanCount * nSamples**2)

    # Return sample frequencies
    time_step = 1. / DIGITIZER_FREQ
    freqs = np.abs( np.fft.fftfreq(len(output), time_step) )
    
    ll = int(len(freqs) / 2) + 1
    x = freqs[int(0.01*ll):ll]
    y = output[int(0.01*ll):ll]
    if len(x) == 0 or len(x) != len(y):
        raise stf.STFException('num freqs %d num powers %d' % (len(x),len(y)))
    noise_spectrum = { 'frequency': x, 'power': y }
    test.measurements.noise_spectrum = noise_spectrum

    # Index of max noise power
    ix = np.argmax( y )
    test.logger.info('max noise %.3e at %.3f MHz' % (y[ix], x[ix]/1.0e6))
    test.measurements.max_noise_power = y[ix]

    # Development use
    if plot:
        import matplotlib.pyplot as plt
        plt.xlabel("Frequency")
        plt.ylabel("Power (A.U.)")
        plt.yscale("log")
        title = '%s-chan%d-dac%d-Power' % (TEST, channel, dac_val)
        plt.title(title)
        plt.semilogy(x, y, "r-")
        plt.savefig(title)
        plt.clf()


stf.register(
    version='1.0',
    run=run_test,
)

if __name__ == "__main__":
    stf.run()
