# STF: Simple Testing Framework

This is the testing framework for the IceCube Upgrade.

## using the framework

### install

stf is python3 compliant and requires `openhtf` and `protoc` libraries. 

**OpenHTF** can be installed with:
`pip[3] install openhtf`

**Protoc** can be installed by following the instructions laid out here:
http://google.github.io/proto-lens/installing-protoc.html

### creating a test

more here soon... but basically a test file only needs to call `register` and `run`

```
import stf

def test_function(test, session):
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

Test config files are JSON documents like this:

```
{
  "args": { ... },
  "expectedValues": { ... },
}
```

For now, they should be placed in `STF_HOME/data/testconfig/<test_name>.json`

### running a test

First, one must add the stf library directory to python path (TODO: instructions)

Then, one can simply run `python <test_file.py>` where test_file is the name of the test you have written.

The framework will automatically name the test after the filename referenced, stripping out the extension and any leading directories

Alternatively you can specify `test_name` to the `stf.register` function.

Test configuration files are located in `STF_HOME/data/testconfig/<test_name>.json`, though one can also manually specify a `test_config='path/to/file'` argument for the register function.
