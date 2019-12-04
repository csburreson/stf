import json

'''
QUESTION XXX: Do we want vars to be global? or based on a testClass or based on a testName? or a mix?


Params
{
    // or maybe this is TestSet (testset)
    test_class: 'FWVersion',
    params: {
        '_global': [
            {'name': 'xxx', 'value': 42}
        ],
        'some_test_phase': {
            'x': 42,
            'y': 100
        },
        'version': {

        }

    }

}

or

{
    test_class: 'FWVersion',
    params: {
        'fw_vnum_test': 42,
        'xxx': 'yyy',
        'foo_min': 0,
        'foo_max': 100
    }
}
'''
global __DB
def getParamDB(datafile='dbdata/params.json', test_config=False):
    global __DB
    if not __DB:
        __DB = ParamDB(datafile, test_config=test_config)
    return __DB


class ParamDB(object):
    def __init__(self, uri, test_config=False):
        # for now, treat uri as a file path
        self.uri = uri
        self._load(uri)

        # could use this to support full db file or just
        # part of a db file
        self.test_config = test_config

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
            self.data[test_name][pname] = pval

    def _addTest(test_name):
        '''
        adds "test_name" to params if it doesn't exist
        '''
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
