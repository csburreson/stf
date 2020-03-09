
#class STFException(

class STFRefuseToRun(Exception):
    '''Used when STF Cannot run, for example if the system time 
    is off and "timesync" is set to "verify"'''
    pass

class STFInvalidArgs(STFRefuseToRun):
    pass

class STFInvalidConfig(STFRefuseToRun):
    pass
