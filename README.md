# STF: Simple Testing Framework

This is the testing framework workspace for the IceCube Upgrade hardware

The stf module lives in `stf/` and includes all the core code that test writers shouldn't have to worry about.

*NOTE*: Currently the included submodule (specifically `python/tools/iceboot`) requires a python2 print statement to be changed to python3. I've modified this in my local env but am not very experienced with submodules and don't think that I should be committing from it... will update soon.


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

After that, set your python path to the stf workspace home -- this will be referred to as `STF_HOME` in the docs -- as such:

```
export PYTHONPATH=$PYTHONPATH:`pwd`
```

This assumes you are in the root directory of this repository.

### creating a test

See the docs:
https://wipacrepo.github.io/stf/test-writing-guide.html

(this is mainly a skeleton... will fill in soon)
https://wipacrepo.github.io/stf/

### debug environment variables

Until STF gets a config, you can override the behaviors of some things with environment variables.

The following variables must be either set (on) or unset (off)
* `STF_DEBUG` - if set, enables `stf.debug` print statements (regardless of -v args)
* `STF_SKIPFW` - if set, skips copying of firmware (for development)
* `STF_FAKEICEBOOT` - if set, creates a fake iceboot object... mainly for framework development
* `STF_ALLOWPRINT=false` - if *SET TO False or 0*, disables printing outside of test functions

Note that the framework will convert any "print" statements within a test into `test.logger.info` statements.

Any print statements outside of your test function (or from iceboot) will show up unless ALLOWPRINT is disabled



