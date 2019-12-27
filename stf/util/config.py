import json
from .misc import flatten, jsonify
from .. import parse
import stf

CONFIG = None

class JsonConfig(object):
    def __init__(self, jsonfile):
        self.jsonfile = jsonfile
        with open(jsonfile, 'r') as f:
            stf.debug(f'f: {jsonfile}')
            conf = parse.json_load(f)
            self._config = conf
            self._flatconfig = flatten(conf)

        self.config = jsonify(conf)
        stf.debug(self.config)

        d = self.config.directories
        if not d.stf_home:
            stf.debug('setting home to {stf.STF_HOME}')
            d.stf_home = stf.STF_HOME
        dirs = d.values()
        # for format?
        config = self.config
        for k, v in d.items():
            if v in dirs:
                try:
                    # format local section placeholders
                    d[k] = v.format(**d)
                except KeyError:
                    # format for placeholders in other sections
                    d[k] = v.format(config=config)

        dv = config.device
        if dv:
            if dv.path:
                dv.path = dv.path.format(config=config)

    def get_dir(self, dirname):
        return self.config.directories[dirname]
        

def get_config(path):
    global CONFIG
    if not CONFIG:
        CONFIG = JsonConfig(path)
    return CONFIG.config
    

        
            
