# Test FPGA SLO_ADC power rail monitors, which exercise D-Egg mainboard ADC1.
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
    stf.Measurement('chan_05').expectPercent(
        "{channel 05 +1V8_A}",
        "{voltage_rail_percent}"),
    stf.Measurement('chan_12').expectPercent(
        "{channel 12 +1V1_power_rail_monitor}",
        "{voltage_rail_percent}"),
    stf.Measurement('chan_13').expectPercent(
        "{channel 13 +1V35_power_rail_monitor}",
        "{voltage_rail_percent}"),
    stf.Measurement('chan_14').expectPercent(
        "{channel 14 +2V5_power_rail_monitor}",
        "{voltage_rail_percent}"),
    stf.Measurement('chan_15').expectPercent(
        "{channel 15 +3V3_power_rail_monitor}",
        "{voltage_rail_percent}"),
)
def run_test(test, session, **kw):
    test.measurements.chan_05 = readSloAdcSingle(test, session,  5)
    test.measurements.chan_12 = readSloAdcSingle(test, session, 12)
    test.measurements.chan_13 = readSloAdcSingle(test, session, 13)
    test.measurements.chan_14 = readSloAdcSingle(test, session, 14)
    test.measurements.chan_15 = readSloAdcSingle(test, session, 15)


stf.register(
    version = '1.0',
    run = run_test,
)


if __name__ == '__main__':
    stf.run()

