
import json

def parseTestWaveform(args):
    if len(args) < 8:
        return None
    wf = {}
    wf["waveformLength"] = (len(args) - 8) / 2
    wf["version"] = (int(args[0]) >> 8) & 0xFF
    wf["channel"] = int(args[0]) & 0xFF
    wf["header1"] = int(args[1])
    wf["header0"] = int(args[2])
    wf["timestamp"] = (long(args[3]) | 
                           (long(args[4]) << 16) | (long(args[5]) << 32))
    wf["waveform"] = []
    wf["thresholdFlags"] = []
    for i in range(wf["waveformLength"]):
        wf["waveform"].append(int(args[7 + 2*i]) >> 2)
        wf["thresholdFlags"].append((int(args[7 + 2*i]) >> 1) & 0x1)
    wf["footer1"] = int(args[-2])
    wf["footer0"] = int(args[-1])
    return wf

def writeWaveformFile(wfs, fileName):
    with open(fileName, "w") as f:
        json.dump(wfs, f)
    
def loadWaveformFile(fileName):
    with open(fileName, "r") as f:
        return json.load(f)
