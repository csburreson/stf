
from optparse import OptionParser, Option, OptionValueError
from . import iceboot_session_cmd
from . import ltc2600
from . import ads4149

modules = [ltc2600, ads4149]


def getParser():
    parser = OptionParser()
    
    iceboot_session_cmd.configureOptions(parser)
    for m in modules:
        m.configureOptions(parser)

    return parser


def startIcebootSession(parser=None, fpgaConfigurationFile=None, host=None, port=None):
    
    if parser is None:
        parser = getParser()
    
    (options, args) = parser.parse_args()
    session = iceboot_session_cmd.init(options,
                            fpgaConfigurationFile=fpgaConfigurationFile,
                            host=host, port=port)

    if session.fpgaVersion() == 0xFFFF:
        print("WARNING: FPGA is NOT CONFIGURED")
    else:
        # Don't init unless FPGA is configured
        for m in modules:
            m.init(options, session)
    
    return session