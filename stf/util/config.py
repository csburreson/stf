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

        self.config = jsonify(conf)



def get_config(path):
    global CONFIG
    if not CONFIG:
        CONFIG = JsonConfig(path)
    return CONFIG.config
    

        
            
