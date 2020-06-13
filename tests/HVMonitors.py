import stf
import time

#HVStabilizationDelay = 0.2
HVStabilizationDelay = 2.0

def readHVmonitors(test, session, channel, HV):
    if HV is not None:
        session.setDEggHV(channel, HV)
    time.sleep(HVStabilizationDelay);
    mon = dict()
    # read HV channel current, EU = volt
    mon['voltage'] = session.sloAdcReadChannel(8+channel*2)
    # read HV channel current, EU = muA
    mon['current'] = session.sloAdcReadChannel(9+channel*2)
    return mon

def cleanup(session):
    session.disableHV(0)
    session.disableHV(0)


def run_test(test, session, channel, HVstart, HVend, HVincrement):
    stf._PRINT('FIXME voltage set delay %f s' % (HVStabilizationDelay))
    cleanup(session)
    time.sleep(HVStabilizationDelay);
    mon = readHVmonitors(test, session, channel, None)
    stf._PRINT('channel-%d HV voltage disabled: voltage: %6.1fv current %5.1fmuA' %
        (channel, mon['voltage'], mon['current']))

    for hv in range(HVstart, HVend+1, HVincrement):
        mon = readHVmonitors(test, session, channel, hv)
        stf._PRINT('channel-%d HV voltage %8.1f: voltage %6.1fV current %5.1fmuA' %
            (channel, hv, mon['voltage'], mon['current']))

    cleanup(session)


stf.register(
    version = '1.0',
    run = run_test,
)


if __name__ == '__main__':
    stf.run()

