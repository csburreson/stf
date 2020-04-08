# Save, validate ADC noise spectrum
# Shamelessly plagiarized from STM32Tools python/DEggTest/adcFFT.py
# by J. Weber

import stf
import numpy as np
#import matplotlib.pyplot as plt

MIN_SAMPLES = 16
MAX_CHANNEL = 1
DIGITIZER_FREQ = 240000000

@stf.measures(
    stf.M('noise_spectrum'),
    stf.M('max_noise_power').expectRange(
        '{noise_power_min}', '{noise_power_max}', type=float))
def run_test(test, session, channel, scanCount, scanSamples):

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

    # Normalize output over scanCount and samples, enabling the same pass/fail
    # criteria to be used over different scanCount, scanSamples args.
    for i in range(len(output)):
        output[i] /= (scanCount * nSamples**2)

    # Return sample frequencies
    time_step = 1. / DIGITIZER_FREQ
    freqs = np.abs( np.fft.fftfreq(len(output), time_step) )
    
    #plt.xlabel("Frequency")
    #plt.ylabel("Power (A.U.)")
    #plt.title("Channel: %s count:%s samples:%d" %
    #   (channel, scanCount, nSamples))
    ll = int(len(freqs) / 2) + 1
    x = freqs[int(0.01*ll):ll]
    y = output[int(0.01*ll):ll]
    if len(x) == 0 or len(x) != len(y):
        raise stf.STFException('num freqs %d num powers %d' % (len(x),len(y)))
    #noise_spectrum = np.stack((x, y))
    noise_spectrum = { 'frequency': x, 'power': y }
    test.measurements.noise_spectrum = noise_spectrum

    # Index of max noise power
    ix = np.argmax( y )
    test.logger.info('max noise %.3e at %.3f MHz' % (y[ix], x[ix]/1.0e6))
    test.measurements.max_noise_power = y[ix]

    #plt.plot(x, y, "r-")
    #plt.show()


stf.register(
    version='1.0',
    run=run_test,
)

if __name__ == "__main__":
    stf.run()
