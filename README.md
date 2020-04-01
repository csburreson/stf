# STF: Simple Testing Framework

This is the testing framework workspace for the IceCube Upgrade hardware

The stf module lives in `stf/` and includes all the core code that test writers shouldn't have to worry about.


## using the framework

### requirements

- **python 3.x** (developed with 3.7.4)
- **openhtf**
- **Protoc**

See the [System Requirements](https://wipacrepo.github.io/stf/system-requirements.html) for more information

NOTE that any test can implicitly add a dependency to the workspace... so be careful 

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

After that, set your python path to the stf workspace home -- this will be referred to as `STF_HOME` in the docs -- as such:

```
export PYTHONPATH=$PYTHONPATH:`pwd`
```

This assumes you are in the root directory of this repository.

### DOCS

https://wipacrepo.github.io/stf/

#### Framework Configuration
[Framework Config](https://wipacrepo.github.io/stf/framework-config.html)

#### Creating and Running single tests
[Test writing guide](https://wipacrepo.github.io/stf/test-writing-guide.html)

[Test Best Practices](https://wipacrepo.github.io/stf/test-best-practices.html)

#### Creating and Running Sets of Tests
[Test Sets](https://wipacrepo.github.io/stf/test-sets.html)

#### Working with Git Submodules
[Git Submodule Hints](https://wipacrepo.github.io/stf/git-submodule-hints.html)

#### Submitting Test Results
[sendresults.py script](https://wipacrepo.github.io/stf/submit.html)

### debug environment variables

Until STF gets a config, you can override the behaviors of some things with environment variables.

The following variables must be either set (on) or unset (off)
* `STF_DEBUG` - if set, enables `stf.debug` print statements (regardless of -v args)
* `STF_SKIPFW` - if set, skips copying of firmware (for development)
* `STF_FAKEICEBOOT` - if set, creates a fake iceboot object... mainly for framework development

Note that the framework will convert any "print" statements within a test into `test.logger.info` statements.

Any print statements outside of your test function (or from iceboot) will show up unless ALLOWPRINT is disabled



