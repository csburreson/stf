import json
from .misc import flatten, jsonify
from .. import parse
import os
import stf

CONFIG = None

class JsonConfig(object):
    def __init__(self, baseconfig, jsonfiles=[]):
        # for js in jsonfile:
        #   misc.update(self._config, conf)
        # 
        self._config = {}
        self._config_files = [baseconfig]
        self._createConfig()
        self.addConfigFile(jsonfiles)
        self._createConfig()


    def addConfigFile(self, jsonfiles):

        if not isinstance(jsonfiles, list):
            jsonfiles = [jsonfiles]
        for f in jsonfiles: 
            if os.path.exists(f):
                self._config_files.append(f)
            else:
                stf.debug(f'Config {f} not found, skipping')

    def _createConfig(self):
        for jsonfile in self._config_files:
            with open(jsonfile, 'r') as f:
                stf.debug(f'parsing config... {jsonfile}')
                conf = parse.json_load(f)
                parse.update(self._config, conf)

        self._flatconfig = flatten(self._config)
        self.settings = jsonify(self._config)
        # settings and config are aliases
        #self.config = self.settings

        d = self.settings.paths
        if not d.stf_home:
            stf.debug(f'setting home to {stf.STF_HOME}')
            d.stf_home = stf.STF_HOME
        dirs = d.values()
        # for format?
        config = self.settings
        for k, v in d.items():
            if v in dirs:
                try:
                    # format local section placeholders
                    d[k] = v.format(config=config, **d)
                except KeyError:
                    # format for placeholders in other sections
                    d[k] = v.format(config=config)

        dv = config.device
        if dv:
            if dv.path:
                dv.path = dv.path.format(config=config)

    def get_path(self, dirname, filename=None):
        if filename:
            return os.path.join(self.settings.paths[dirname], filename)
        return self.settings.paths[dirname]

        
    def getIcebootOpts(self):
        return dict(
            host=self.settings.iceboot.host,
            port=self.settings.iceboot.port,
            debug=self.settings.iceboot.debug,
        )
     
    def setIcebootOpts(self, host=None, port=None, debug=None):
        if host:
            self.settings.iceboot.host = host
        if port:
            self.settings.iceboot.port = port
        if debug:
            self.settings.iceboot.debug = debug
        


def get_config(path='stfconfig.json', optional=['stfconfig.local.json']):
    global CONFIG
    if CONFIG:
        return CONFIG
    CONFIG = JsonConfig(path, jsonfiles=optional)
    return CONFIG
    

        
            
