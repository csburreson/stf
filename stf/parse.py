"""
json_minify shamelessly stolen from: https://github.com/getify/JSON.minify/

https://getify.mit-license.org/

A port of the `JSON-minify` utility to the Python language.

Based on JSON.minify.js: https://github.com/getify/JSON.minify

Contributers:
  - Gerald Storer
    - Contributed original version
  - Felipe Machado
    - Performance optimization
  - Pradyun S. Gedam
    - Conditions and variable names changed
    - Reformatted tests and moved to separate file
    - Made into a PyPI Package
"""

import re
import os
import json
from .debug import DEBUG, debug
import stf
import collections.abc
from copy import deepcopy as dc

class SetConfigException(Exception):
    pass

def verify_config(testConfig, instanceConfig):
    inst = instanceConfig['instance']
    # XXX: this was meant to collect all the errors, but
    # needs to be reimplemented
    errors = []
    try:
        if testConfig['args'] and 'args' in instanceConfig:
            has_key_subset(testConfig['args'], instanceConfig['args'])
        if testConfig['expectedValues'] and 'expectedValues' in instanceConfig:
            has_key_subset(testConfig['expectedValues'], instanceConfig['expectedValues'])
    except AssertionError as e:
        errors.append(str(e))
        stf.debug(f'Error: {e}')

    if errors:
        raise SetConfigException('Invalid overrides in instance config \'{}\': \n{}'.format(inst, '\n\t'.join(errors)))

    stf.debug(f'Config is VALID for instance {inst}')

    return {
        "args": update(testConfig['args'], instanceConfig.get('args', {})),
        "expectedValues": update(testConfig['expectedValues'], instanceConfig.get('expectedValues', {}))
    }


def has_key_subset(superset, subset):
    '''given a dictionary, compare the keys in another dict recursively to make
    sure they exist'''
    for k, v in subset.items():
        assert k in superset.keys(), f'''key '{k}' not found in testconfig dict: {superset}'''
        if isinstance(v, dict):
            has_key_subset(superset[k], v)
    

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class SetConfig(object):
    def __init__(self, config_file, set_name):
        self.config_file = config_file
        self.set_name = set_name
        debug(f'conf for {set_name}: {config_file}')
        with open(config_file, 'r') as f:
            self._config = json_load(f)

        if not 'tests' in self._config:
            raise Exception("Invalid test config. Missing 'tests' key")

        self.instances = []

        if isinstance(self._config['tests'], list):
            self.is_test_list = True
            self.tests = self._config['tests']
            self.testDict = {k: [] for k in self._config['tests']}
            debug("\nHERE")
        else:
            self.is_test_list = False
            self.tests = self._config['tests'].keys()
            self.testDict = self._config['tests']
        debug('(SetConfig) tests: {}'.format(self.tests))
        debug('\nSETCONFIG')

    def configure(self):
        #self.instances = []
        stf.debug('setconfig->configure')
        for testName, test_instances in self.testDict.items():
            # test_instances can be empty
            registered = stf.getRegisteredClass(testName)
            debug(f'verifying instance configs for test {testName}')
            for ti in test_instances:
                inst = ti['instance']
                if inst == 'base':
                    #debug('base instance; using test params:')
                    if ti.get('args') or ti.get('expectedValues'):
                        raise SetConfigException('Base instances cannot have overrides')
                    mergedConfig = dc(registered.getTestParams())
                    #debug(f"  args: {mergedConfig['args']}\n  expv: {mergedConfig['expectedValues']}")
                else:
                    #debug(f' checking {testName}:{ti["instance"]}')
                    mergedConfig = verify_config(dc(registered.getTestParams()), ti)
                self.instances.append({
                    'test_name': testName,
                    'testinstance_name': f'{testName}:{inst}',
                    'instance_name': inst,
                    'args': mergedConfig['args'],
                    'expectedValues': mergedConfig['expectedValues']
                })
            if not test_instances:
                debug('no instances, appending base instance')
                ps = registered.getTestParams()
                self.instances.append({
                    'test_name': testName,
                    'testinstance_name': testName,
                    'instance_name': 'base',
                    'args': ps.get('args', {}),
                    'expectedValues': ps.get('expectedValues', {})
                })


def json_loads(s):
    if not DEBUG.NOSTRIPJSON:
        s = json_minify(s)  
        debug('minify: {}'.format(s))
    return json.loads(s)


def json_load(f):
    return json_loads(f.read())

# Shamelessly stolen from: https://github.com/getify/JSON.minify/
def json_minify(string, strip_space=True):
    tokenizer = re.compile('"|(/\*)|(\*/)|(//)|\n|\r')
    end_slashes_re = re.compile(r'(\\)*$')

    in_string = False
    in_multi = False
    in_single = False

    new_str = []
    index = 0

    for match in re.finditer(tokenizer, string):

        if not (in_multi or in_single):
            tmp = string[index:match.start()]
            if not in_string and strip_space:
                # replace white space as defined in standard
                tmp = re.sub('[ \t\n\r]+', '', tmp)
            new_str.append(tmp)
        elif not strip_space:
            # Replace comments with white space so that the JSON parser reports
            # the correct column numbers on parsing errors.
            new_str.append(' ' * (match.start() - index))

        index = match.end()
        val = match.group()

        if val == '"' and not (in_multi or in_single):
            escaped = end_slashes_re.search(string, 0, match.start())

            # start of string or unescaped quote character to end string
            if not in_string or (escaped is None or len(escaped.group()) % 2 == 0):  # noqa
                in_string = not in_string
            index -= 1  # include " character in next catch
        elif not (in_string or in_multi or in_single):
            if val == '/*':
                in_multi = True
            elif val == '//':
                in_single = True
        elif val == '*/' and in_multi and not (in_string or in_single):
            in_multi = False
            if not strip_space:
                new_str.append(' ' * len(val))
        elif val in '\r\n' and not (in_multi or in_string) and in_single:
            in_single = False
        elif not ((in_multi or in_single) or (val in ' \r\n\t' and strip_space)):  # noqa
            new_str.append(val)

        if not strip_space:
            if val in '\r\n':
                new_str.append(val)
            elif in_multi or in_single:
                new_str.append(' ' * len(val))

    new_str.append(string[index:])
    return ''.join(new_str)
