import json

def getParamDB(local=False):
    return ParamDB('db/params.json')


class ParamDB(object):
    def __init__(self, uri):
        # for now, treat uri as a file path
        self.uri = uri
        self._load(uri)

    def _load(self, uri):
        with open(uri, 'r') as f:
            self.data = json.load(f)
            
    def getTestParams(self, test_name, param_list):
        ret = {}
        params = self.data.get(test_name, {})
        for p in param_list:
            ret[p] = params[p]
        return ret

    def setTestParams(self, test_name, param_map):
        self._addTest(test_name)
        self.data[test_name] = param_map

    def addTestParams(self, test_name, param_map):
        '''
        add params as a dict of key -> value for test_name

        i.e.
        addTestParams('fooTest', {'bar': 42, 'nar': 100})
        '''
        self._addTest(test_name)
        for pname, pval in param_map.items():
            self.data[test_name]

    def _addTest(test_name):
        if test_name not in self.data:
            self.data[test_name] = {}

    def addTestParam(self, test_name, pname, pval):
        self.data[test_name][pname] = pval
        self._save()

    def _save(self):
        '''
        don't call me!
        '''
        with open(self.uri, 'w') as f:
            json.dump(self.data, f, indent=2)

    '''
    @staticmethod
    def getTestParam(test_name, param_list):
        DB_PARAMS = {
            'fw_vnum_test': {
                'expected_fw_vnum': '0x6a'
            },
            'foo': {
                'min': 40,
                'max': 44
            }
        }
        ret = {}
        for p in param_list:
            ret[p] = DB_PARAMS[test_name][p]
        return ret
    '''
