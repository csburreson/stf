
from .test_waveform import parseTestWaveform
from optparse import OptionParser
import ymodem
import socket
import fcntl
import os
import time
import select
import numpy as np

PROMPT = "\r\n> \n"


def stripStackSize(s):
    ll = len(s.split()[0])
    return s[(ll + 1):]


class IcebootSessionCmd(object):
    
    def __init__(self, comms, debug, fpgaConfigurationFile=None):
        self.comms = comms
        self.debug = debug
        self.cmd("true setecho\r\n")
        time.sleep(0.1)
        # Clear the buffer
        while True:
            try:
                comms.recv(128)
            except:
                break
        # Clear the stack
        cnt = int(self.cmd(".s").split()[0].replace("<", "").replace(">", ""))
        for _ in range(cnt):
            self.cmd("drop")

        if fpgaConfigurationFile is not None:
            self.ymodemConfigureCycloneFPGA(fpgaConfigurationFile)

        print("New IceBoot session: FPGA version %x Software version %x" %
                                (self.fpgaVersion(), self.softwareVersion()))

    def cmd(self, cmdStr, timeout=1):
        """
        Send cmdStr to Iceboot and return the response as a string
        """
  
        output = self.raw_cmd(cmdStr, timeout=timeout).decode()
        
        if self.debug:
            print("Received %s" % output)

        return output

    def uint16_cmd(self, cmdStr, n_words):
        ''' Send a command to Iceboot and return the response 
        as a tuple of ints 
        n_words is the number of expected words
        '''

        # 2 bytes per 16 bit word
        buff = self.raw_cmd(cmdStr, 2*n_words)        

        unpacked_response = np.frombuffer(buff, np.uint16)

        if self.debug:
            print("Received %s" % str(unpacked_response))

        return unpacked_response


    def raw_cmd(self, cmdStr, n_bytes=None, timeout=1):
        ''' Sends a command and returns the response as a binary buffer
            if n_bytes is not None, raw_cmd will not return unless
            n_bytes have been read from the socket 
            (not including the echo or the prompt) 
        ''' 
        if self.debug:
            print("SENT: %s" % cmdStr)

        if not cmdStr.endswith("\r\n"):
            cmdStr += "\r\n"

        self.comms.send(cmdStr.encode())
        
        # nbytes to read including the cmdStr and the prompt
        if n_bytes is not None:
            n_bytes_adj = n_bytes + len(PROMPT) + len(cmdStr)

        reply = bytearray()
        while True:        
            new_data = self._read_next(timeout=timeout)
            reply.extend(new_data)
            
            if n_bytes is None or len(reply) >= n_bytes_adj:
                try:
                    if reply[-len(PROMPT):].decode() == PROMPT:
                        break     
                except UnicodeDecodeError:
                    pass

        # Strip original command and prompt and return the reply
        reply = reply[len(cmdStr):-len(PROMPT)]

        return reply        


    def _read_next(self, n_bytes=128, timeout=1):
        rdy = select.select([self.comms], [], [], timeout)        

        if rdy[0]:
            recv_bytes = self.comms.recv(n_bytes)

            return recv_bytes
        else:
            raise IOError('Timeout!')
 
    def _read_n(self, n_bytes):
        buf = bytearray()
        while len(buf) < n_bytes:
            buf.extend(self._read_next(n_bytes - len(buf)))
            
        return buf

    def fpgaVersion(self):
        return int(stripStackSize(self.cmd("fpgaVersion .s drop")))
    
    def softwareVersion(self):
        return int(stripStackSize(self.cmd("softwareVersion .s drop")))

    def domClock(self):
        val = stripStackSize(self.cmd("domClock .s drop drop")).split()
        return ( (long(val[0]) & 0xFFFFFFFF) | 
                 ((long(val[1]) & 0xFFFFFFFF) << 32))

    def fpgaWrite(self, addr, data):
        cmd = ""
        for s in data:
            cmd += "%s " % s
        cmd += "%s %s fpgaWrite" % (len(data), addr)
        self.cmd(cmd)

    def fpgaRead(self, addr, len):
        return [int(s) for s in
                     self.cmd("%s %s printFPGA" % (len, addr)).split()]

    def fpgaDump(self, adr, length):
        return self.uint16_cmd('%d %d dumpFPGA\r\n' % (length, adr), length)

    def testDEggCPUTrig(self, channel):
        self.cmd("%s testDEggCPUTrig" % channel)

    def testDEggThresholdTrig(self, channel, threshold):
        self.cmd("%s %s testDEggThresholdTrig" % (channel, threshold))
    
    def testDEggWaveformReadout(self):
        # Note: 0xDFE contains the last address written, so length is one more
        n_words = 1 + self.fpgaRead(0xDFE, 1)[0]
        return parseTestWaveform(self.fpgaDump(0, n_words))        

    def startDEggSWTrigStream(self, channel, period_in_ms):
        cmd = '%d %d 1 DEggWfmStream\r\n' % (channel, period_in_ms)
        self.comms.send(cmd.encode())

        got = ''
        while True:
            # read one byte at a time to ensure we don't 
            # consume the beginning of a waveform
            got += self._read_next(1).decode()

            if got.endswith('BEGIN STREAM\r\n'):
                # found beginning of waveform stream                
                break

    def startDEggThreshTrigStream(self, channel, threshold):
        cmd = '%d %d 0 DEggWfmStream\r\n' % (channel, threshold)
        self.comms.send(cmd.encode())

        got = ''
        while True:
            got += self._read_next(1).decode()

            if got.endswith('BEGIN STREAM\r\n'):
                # found beginning of waveform stream                
                break

    def readWFMFromStream(self):
        ''' result is returned as an array of uint16s'''
        len_bytes = self._read_n(2)

        n_words = np.frombuffer(len_bytes, np.uint16)[0]

        # 2 bytes per 16 bit word
        wfm_buff = self._read_n(2*n_words)

        return np.frombuffer(wfm_buff, np.uint16)


    def endStream(self):
        # this message could be anything;
        # sending any data ends the stream
        self.comms.send('STOP\r\n'.encode())

        # empty out the rcv buffer
        while True:
            try:
                self._read_next(timeout=0.1)
            except IOError:
                break


    def setDEggConstReadout(self, channel, preConfig, nSamples):
        self.cmd("%s %s %s setDEggConstReadout" %
                                          (channel, preConfig, nSamples))

    def setDEggVariableReadout(self, channel, preConfig, postConfig):
        self.cmd("%s %s %s setDEggVariableReadout" %
                                          (channel, preConfig, postConfig))

    def readFlashInterlock(self):
        return int(stripStackSize(self.cmd("readFlashInterlock .s drop"))) == 1

    def readFPGAConfigInterlock(self):
        return int(stripStackSize(
                           self.cmd("readFPGAConfigInterlock .s drop"))) == 1

    def readLIDInterlock(self):
        return int(stripStackSize(self.cmd("readLIDInterlock .s drop"))) == 1

    def readHVInterlock(self):
        return int(stripStackSize(self.cmd("readHVInterlock .s drop"))) == 1

    def memtest(self):
        return self.cmd("memtest")

    def resetDAC(self):
        self.cmd("resetDAC")

    def enableHV(self, channel):
        self.cmd("%s enableHV")

    def disableHV(self, channel):
        self.cmd("%s disableHV")

    def setDAC(self, channel, value):
        """
        Set DAC value according to channel letter, e.g. 'A'
        """
        self.cmd("%d %d setDAC" % (ord(channel), value))

    def resetADS4149(self, channel):
        self.cmd("%d resetADS4149" % channel)

    def writeADS4149(self, channel, register, value):
        self.cmd("%d %d %d writeADS4149" % (channel, register, value))
    
    def readADS4149(self, channel, register):
        ret = self.cmd("%d %d readADS4149 .s drop" % (channel, register))
        return int(stripStackSize(ret))

    def _ymodemSend(self, infile, cmd):
        infile = os.path.expanduser(infile)
        if not os.path.exists(infile):
            print("File \"%s\" does not exist" % infile)
            return
        encodedCmd = cmd.encode()
        self.comms.send(encodedCmd)
        self._read_n(len(encodedCmd))
        ymodem.ymodemImpl(self.comms.fileno(), infile, verbose=False)
        # Remove partial prompt
        prompt = "> \n"
        ret = ""
        while not ret.endswith(prompt):
            try:
                ret +=  self.comms.recv(128).decode()
            except:
                pass

    def ymodemConfigureCycloneFPGA(self, infile):
        cmd = "ymodemConfigureCycloneFPGA\r\n"
        self._ymodemSend(infile, cmd)

    def flashID(self):
        return self.cmd("flashID")

    def flashRemove(self, remoteFileName):
        cmdstr = "s\" %s\" flashRemove" % remoteFileName
        self.cmd(cmdstr)

    def flashClear(self):
        self.cmd("flashClear")

    def ymodemFlashUpload(self, remoteFileName, infile):
        cmd = "s\" %s\" ymodemFlashUpload\r\n" % remoteFileName
        self._ymodemSend(infile, cmd)

    def flashConfigureCycloneFPGA(self, remoteFileName, timeout=10):
        cmdstr = "s\" %s\" flashConfigureCycloneFPGA" % remoteFileName
        self.cmd(cmdstr, timeout=timeout)

    def flashLS(self):
        outstr = self.cmd("flashLS")
        # Get the categories from the first line
        out = []
        lines = outstr.splitlines()
        if len(lines) == 0:
            return out
        categories = lines[0].split()
        if len(categories) == 0:
            return out
        # Skip the first two lines
        for line in lines[2:]:
            data = line.split()
            if len(data) != len(categories):
                continue
            entry = {}
            for i in range(len(categories)):
                entry[categories[i]] = data[i]
            out.append(entry)
        return out


def configureOptions(parser):
    # Only support Ethernet host/port at the moment
    parser.add_option("--host", dest="host", help="Ethernet host name or IP",
                      default="192.168.0.10")
    parser.add_option("--port", dest="port", help="Ethernet port",
                      default="5012")
    parser.add_option("--debug", dest="debug", action="store_true",
                      help="Print board I/O stdout", default=False)
    parser.add_option("--fpgaConfigurationFile", dest="fpgaConfigurationFile",
                      help="FPGA configuration file", default=None)


def init(options, fpgaConfigurationFile=None, host=None, port=None):
    # Default now is socket.  Add interfaces as needed
    #print str(locals())
    session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if host is None:
        host = options.host
    if port is None:
        port = options.port
    session.connect((host, int(port)))
    fcntl.fcntl(session, fcntl.F_SETFL, os.O_NONBLOCK)
    if fpgaConfigurationFile == None:
        fpgaConfigurationFile = options.fpgaConfigurationFile
    return IcebootSessionCmd(session, options.debug,
                        fpgaConfigurationFile=fpgaConfigurationFile)
