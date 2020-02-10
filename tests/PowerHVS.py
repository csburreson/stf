# Test FPGA SLO_ADC power HVS monitors, which exercise D-Egg mainboard ADC1.
# ADS8332 analog to digital converters.
# original author JWeber

import stf

# Read single chanel of SLO ADC data.
# returns: SLO ADC single channel data, unparsed
def readSloAdcSingleChannel(test, session, channel):
    cmd = str(channel) + " sloAdcReadChannel"
    #stf._PRINT(cmd)
    output = session.cmd(cmd)
    #stf._PRINT(output)
    if output is None:
        test.logger.error("Read session.cmd '%s' failure" % (cmd))
        return None

    test.logger.info(output)    # TODO necessary?
    return output

# Parse SLO ADC read output. Return calibrated 
# sample intput:
# "channel  3 LVS_SLO_IMON_2V5                    0 mA    SATURATED"
# returns: floating point calibrated output, or None if error
def parseSloAdc(test, session, channel, line):
    word = line.split()
    if (len(word) < 5):
        #test.logger.error("Channel %d parsing error" % (channel))
        stf._PRINT("Channel %d parsing error" % (channel))
        return None

    readChan = int(word[1], 10)

    if (readChan != channel):
        test.logger.error("Read channel %d, got channel %d"
            % (channel, readChan))
        return None

    if (line.find('SATURATED') != -1): 
        test.logger.error("Channel %d saturated" % (channel))
        return None

    return float(word[3])

# Read single channel of SLO ADC data.
# returns: SLO ADC single channel data, parsed
def readSloAdcSingle(test, session, channel):
    return parseSloAdc(test, session, channel,
        readSloAdcSingleChannel(test, session, channel))

# Test SLO_ADC single channel reads.
@stf.measures(
    stf.Measurement('chan_08').expectPercent(
        "{channel 08 SLO_HVS0_VMON}",
        "{voltage_rail_percent}"),
    stf.Measurement('chan_09').expect(
        "{channel 09 SLO_HVS0_IMON}"),
    stf.Measurement('chan_10').expectPercent(
        "{channel 10 SLO_HVS1_VMON}",
        "{voltage_rail_percent}"),
    stf.Measurement('chan_11').expect(
        "{channel 11 SLO_HVS1_IMON}"),
)
def run_test(test, session, **kw):
    test.measurements.chan_08 = readSloAdcSingle(test, session,  8)
    test.measurements.chan_09 = readSloAdcSingle(test, session,  9)
    test.measurements.chan_10 = readSloAdcSingle(test, session, 10)
    test.measurements.chan_11 = readSloAdcSingle(test, session, 11)


stf.register(
    version = '1.0',
    run = run_test,
)


if __name__ == '__main__':
    stf.run()

