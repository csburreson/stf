# Test FPGA SLO_ADC functions, which exercise D-Egg mainboard ADC0, ADC1
# ADS8332 analog to digital converters.
# original author JWeber

import stf

# Parse SLO ADC read output. Return calibrated 
# sample intput:
# "channel  3 LVS_SLO_IMON_2V5                    0 mA    SATURATED"
# returns: floating point calibrated output, or None if error
def readSloAdc(test, session, channel):
    cmd = str(channel) + " sloAdcReadChannel"
    #stf._PRINT(cmd)
    output = session.cmd(cmd)
    #stf._PRINT(output)
    if output is None:
        test.logger.error("Read session.cmd '%s' failure" % (cmd))
        return None

    test.logger.info(output)

    word = output.split()
    if (len(word) < 5):
        test.logger.error("Channel %d parsing error" % (channel))
        return None

    readChan = int(word[1], 10)
    if (readChan != channel):
        test.logger.error("Read channel %d, got channel %d"
            % (channel, readChan))
        return None

    if (output.find('SATURATED') != -1): 
        test.logger.error("Channel %d saturated" % (channel))
        return None

    return float(word[3])

    
# Test SLO_ADC single channel reads.
@stf.measures(
    stf.Measurement('chan_00').expect(
        "{channel 00 LVS_SLO_IMON_1V1}"), 
    stf.Measurement('chan_01').expect(
        "{channel 01 LVS_SLO_IMON_1V35}"),
    stf.Measurement('chan_02').expect(
        "{channel 02 LVS_SLO_IMON_1V8}"),
    stf.Measurement('chan_03').expect(
        "{channel 03 LVS_SLO_IMON_2V5}"),
    stf.Measurement('chan_04').expect(
        "{channel 04 LVS_SLO_IMON_3V3}"),
    stf.Measurement('chan_05').expectPercent(
        "{channel 05 +1V8_A}",
        "{voltage_rail_percent}"),
    stf.Measurement('chan_06').expectRange(
        "{channel 06 light_sensor_dark_min}",
        "{channel 06 light_sensor_dark_max}",
        type=float),
    stf.Measurement('chan_07').expectRange(
        "{channel 07 temperature_room_min}",
        "{channel 07 temperature_room_max}",
        type=float),
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
def test_single_channel(test, session, **kw):
    test.measurements.chan_00 = readSloAdc(test, session,  0)
    test.measurements.chan_01 = readSloAdc(test, session,  1)
    test.measurements.chan_02 = readSloAdc(test, session,  2)
    test.measurements.chan_03 = readSloAdc(test, session,  3)
    test.measurements.chan_04 = readSloAdc(test, session,  4)
    test.measurements.chan_05 = readSloAdc(test, session,  5)
    test.measurements.chan_06 = readSloAdc(test, session,  6)
    test.measurements.chan_07 = readSloAdc(test, session,  7)
    test.measurements.chan_08 = readSloAdc(test, session,  8)
    test.measurements.chan_09 = readSloAdc(test, session,  9)
    test.measurements.chan_10 = readSloAdc(test, session, 10)
    test.measurements.chan_11 = readSloAdc(test, session, 11)
    test.measurements.chan_12 = readSloAdc(test, session, 12)
    test.measurements.chan_13 = readSloAdc(test, session, 13)
    test.measurements.chan_14 = readSloAdc(test, session, 14)
    test.measurements.chan_15 = readSloAdc(test, session, 15)


stf.register(
    version = '1.0',
    run = test_single_channel,
    test_desc = "SLO ADC single channel reads",
)


if __name__ == '__main__':
    stf.run()

