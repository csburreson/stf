# STF: Simple Testing Framework

This is the testing framework for the IceCube Upgrade hardware

## using the framework

### install

stf is python3 compliant and requires `openhtf` and `protoc` libraries. 

**OpenHTF** can be installed with:
`pip[3] install openhtf`

**Protoc** can be installed as such:

For Linux:
```
PROTOC_ZIP=protoc-3.7.1-linux-x86_64.zip
curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v3.7.1/$PROTOC_ZIP
sudo unzip -o $PROTOC_ZIP -d /usr/local bin/protoc
sudo unzip -o $PROTOC_ZIP -d /usr/local 'include/*'
rm -f $PROTOC_ZIP
```
See 
http://google.github.io/proto-lens/installing-protoc.html

for more information, or installing in non-linux envs.

### creating a test

more here soon... but basically a test file only needs to call `register` and `run`

The register function minimally needs a "version" string and a "run" function as arguments.

The function passed to run *MUST* take **test** and **session** as its first two positional arguments.

Additional arguments can be specified in the test config.

**XXX: for now, the test_function must also accept `**kwargs`**

```
import stf

@stf.test
def test_function(test, session, **kw):
  pass
  
stf.register(
  version='1.0',
  run=test_function
)

if __name__ == '__main__':
  stf.run()
```

For now, place tests in STF_HOME/tests where stf home is the root of this repository.

The framework code all lives in the **library directory** as a python module: `STF_HOME/stf/`

** Test Config **

A test config file is **required** for all tests even if it's empty

Test config files are JSON documents like this:

```
{
  "args": {},
  "expectedValues": {},
}
```

For now, they should be placed in `STF_HOME/data/testconfig/<test_name>.json`

`args` and `expectedValues` are passed to tests as python keyword args; one can mention them by name in the test definition or use the `**kw` dictionary.

### running a test

First, one must add the stf library directory to python path. 

STF_HOME is used to denote the location of this repository on your system

You must also add the stf module's `tools/python` directory:

`export PYTHONPATH=$PYTHONPATH:<STF_HOME_PATH>:<STF_HOME_PATH>/stf/tools/python`

Then, one can simply run `python <test_file.py>` where test_file is the name of the test you have written.

The framework will automatically name the test after the filename referenced, stripping out the extension and any leading directories

Alternatively you can specify `test_name` to the `stf.register` function.

Test configuration files are located in `STF_HOME/data/testconfig/<test_name>.json`, though one can also manually specify a `test_config='path/to/file'` argument for the register function.

### measuring values

If a test declares that it is measuring a value, the test will fail if the measurement is not recorded in `test.measurements`

You can declare a measurement as such:
```
import stf

@stf.measures(stf.Measurement('foo'))
def test_function(test, session, **kw):
  test.measurements.foo = 'bar'
  
stf.register(
  version='1.0',
  run=test_function
)

if __name__ == '__main__':
  stf.run()
```

#### validators

Here's an example of measuring a value and requiring it be in a range; this test would pass:

```
@stf.measures(stf.Measurement('foo').in_range(0, 100))
def test_function(test, session, **kw):
    test.measurement.foo = 42
```

Here's an example of measuring a value and requiring it equal a particular value; this test would pass if `blah()` returns 42:
```
@stf.measures(stf.Measurement('foo').equals(42))
def test_function(test, session, **kw):
    x = blah()
    test.measurement.foo = x
```

#### validating with arguments (expected values)

For validating measurements with an argument provided in a testconfig, specify the name of the parameter with the `equalsParam` decorator:
```
@stf.measures(stf.Measurement('foo').equalsParam('{bar}'))
def test_function(test, session, **kw):
    test.measurement.foo = 42
```

```
{
  "args": {},
  "expectedValues": {
    "bar": 42
  }
}
```

The above test would pass since the `test.measurement.foo` value equals the `expectedValues.bar` config value.

Similarly, one can use a range validator as such: **XXX TODO**
