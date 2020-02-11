# Test FPGA SLO_ADC power LVS monitors, which exercise D-Egg mainboard ADC0.
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
    stf.Measurement('chan_00').expectPercent(
        "{channel 00 LVS_SLO_IMON_1V1}",
        "{current_percent}"),
    stf.Measurement('chan_01').expectPercent(
        "{channel 01 LVS_SLO_IMON_1V35}",
        "{current_percent}"),
    stf.Measurement('chan_02').expectPercent(
        "{channel 02 LVS_SLO_IMON_1V8}",
        "{current_percent}"),
    stf.Measurement('chan_03').expectPercent(
        "{channel 03 LVS_SLO_IMON_2V5}",
        "{current_percent}"),
    stf.Measurement('chan_04').expectPercent(
        "{channel 04 LVS_SLO_IMON_3V3}",
        "{current_percent}"),
)
def run_test(test, session, **kw):
    test.measurements.chan_00 = readSloAdcSingle(test, session,  0)
    test.measurements.chan_01 = readSloAdcSingle(test, session,  1)
    test.measurements.chan_02 = readSloAdcSingle(test, session,  2)
    test.measurements.chan_03 = readSloAdcSingle(test, session,  3)
    test.measurements.chan_04 = readSloAdcSingle(test, session,  4)


stf.register(
    version = '1.0',
    run = run_test,
)


if __name__ == '__main__':
    stf.run()

