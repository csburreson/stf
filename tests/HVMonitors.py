# Vary channel commanded high voltage. Verify associated high voltage supply
# voltage and current monitor values.
#
# All voltage engineering units are volts, v.
# All current engineering units are microAmperes, muA.
#
# Original author J. Weber

# TODO add light sensor reading if PMT installed

import stf
import time
import numpy as np

HVenabled = None # HV enabled state cache

def r2(x, y, model):
    """ Calculate linear regression Coefficient of determination or "R Squared".
        Essentially a quality of fit: (worse) 0 <= r2 <= 1.0 (better)
    """
    yhat = model(x)
    ybar = np.sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)
    sstot = np.sum((y - ybar)**2)
    if sstot == 0.0:
        raise stf.STFException('Liner regression R2 calculation: Vmons are 0')

    r2 = ssreg / sstot

    return r2


def readHVmonitors(test, session, channel, delay, HV):
    """ Return HV monitor values in volts, muA """
    global HVenabled
    if HV is None:
        if HVenabled is None or HVenabled:
            session.disableHV(channel)
            HVenabled = False
        session.setDEggHV(channel, 0)
    else:
        if HVenabled is None or not HVenabled:
            session.enableHV(channel)
            HVenabled = True
        session.setDEggHV(channel, HV)
 
    time.sleep(delay); # voltage change stabilization

    v = session.sloAdcReadChannel(8+channel*2)
    muA = session.sloAdcReadChannel(9+channel*2)

    return v, muA


def cleanup(session):
    """ Cleanup hardware config, session """
    session.disableHV(0)
    session.disableHV(1)
    HVenabled = False


@stf.measures(stf.M('HVS_Monitors'),
              stf.M('HVS_VMon_Fit_R2').expectRange(
                  '{HVS_VMon_Fit_R2_min}', '{HVS_VMon_Fit_R2_max}', type=float),
              stf.M('HVS_VMon_Fit_Slope').expectRange(
                  '{HVS_VMon_Fit_Slope_min}',
                  '{HVS_VMon_Fit_Slope_max}', type=float),
              stf.M('HVS_Imon').expectRange(
                  '{HVS_IMon_min}',
                  '{HVS_IMon_max}', type=float)
             )
def run_test(   test, session, channel, HVstart, HVend, HVincrement,
                HVStabilizationDelay, plot=False):
    """ Main test driver. """

    HVInterlock = session.readHVInterlock()
    test.logger.info('read HV interlock: %d' % (HVInterlock))
    if not HVInterlock:
        raise stf.STFException("HV Interlock is disabled")

    # TODO add light sensor read here if PMTs installed.

    HVS_V_Cmd = []
    HVS_V_Mon = []
    HVS_I_Mon = []

    cleanup(session)

    v, muA = readHVmonitors(test, session, channel, HVStabilizationDelay, None)
    session.enableHV(channel)
    HVenabled = True

    for hv in range(HVstart, HVend+1, HVincrement):
        v, muA = readHVmonitors(test, session, channel, HVStabilizationDelay,hv)
        HVS_V_Cmd.append(hv)
        HVS_V_Mon.append(v)
        HVS_I_Mon.append(muA)

    cleanup(session)

    # Stop if V monitors are all zero. This can happen if HV board is not
    # installed
    if not np.any(HVS_V_Mon):
        raise stf.STFException('HV V monitors are 0.0')

    HV_V_Coef = np.polyfit(HVS_V_Cmd, HVS_V_Mon, 1)
    HV_V_Fn = np.poly1d(HV_V_Coef)
    HV_V_r2 = r2(HVS_V_Cmd, HVS_V_Mon, HV_V_Fn)

    if plot:
        import matplotlib.pyplot as plt
        plt.xlabel("HV Command, V")
        plt.plot(HVS_V_Cmd, HVS_V_Mon, 'bo', label='voltage monitor, v')
        plt.plot(HVS_V_Cmd, HV_V_Fn(HVS_V_Cmd), 'b:', label='voltage fit, v')
        plt.plot(HVS_V_Cmd, HVS_I_Mon, 'ro', label='current monitor, muA')
        plt.legend()
        plt.show()

    HVS_Monitors = dict()
    HVS_Monitors['set_voltage'] = HVS_V_Cmd
    HVS_Monitors['meas_voltage'] = HVS_V_Mon
    HVS_Monitors['meas_current'] = HVS_I_Mon
    HVS_Monitors['fit_voltage'] = HV_V_Fn(HVS_V_Cmd)

    test.measurements.HVS_Monitors = HVS_Monitors
    test.measurements.HVS_VMon_Fit_R2 = HV_V_r2
    test.measurements.HVS_VMon_Fit_Slope = HV_V_Coef[0]
    test.measurements.HVS_Imon = max( HVS_I_Mon )


stf.register(
    version = '1.0',
    run = run_test,
)


if __name__ == '__main__':
    stf.run()

