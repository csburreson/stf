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
