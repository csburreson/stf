# How To Run a STF test

The document details how to run a single STF test. To run an aggregation of
tests, see the [test set](test-sets.md) documentation.

## Installation
First [install](installation.md) STF.

## Running a test

For simplicity, run tests from the `STF_HOME` directory, i.e the root of the STF cloned
workspace. STF searches for and used Python modules, so the `PYTHONPATH` must include the
`STF_HOME` location. For example:
```
$ cd stf
stf $ export PYTHONPATH=`pwd`
```

To run a test, simply invoke the python file containing the test and register call as such:

`$ python tests/CheckFirmware.py`

All tests require Python3. 
For systems where the default `python` binary is python2, the test should
explicitly invoke the `python3` binary:

`$ python3 tests/CheckFirmware.py`

Test arguments include:
* `-v[vv]` output verbosity
* `--testconfig` path to alternative test configuration file (instead of using default or "registered" file)
* `--prodid` or `--mbsnum` -- add a "Production ID" or MB Serial Number (same option) to the test results, which may be ingested by a database.
* `--meta k=v [k2=v2...]` add an arbitrary number of key=value metadata bits to the results output (note that everything after --meta will be interpreted as key=value). These also adds the meta information to the test results, which may be ingested by a database.

Also note that all unused arguments will also appear in the results output

## Debug Environment Variables

You can override the behaviors of some things with environment variables.

The following variables must be either set (on) or unset (off)
* `STF_DEBUG` - if set, enables `stf.debug` print statements (regardless of -v args)
* `STF_SKIPFW` - if set, skips copying of firmware (for development)
* `STF_FAKEICEBOOT` - if set, creates a fake iceboot object... mainly for framework development

Note that the framework will convert any "print" statements within a test into `test.logger.info` statements.

Any print statements outside of your test function (or from iceboot) will show up unless ALLOWPRINT is disabled

## Test Outcomes (pass/fail/error/timeout)

An STF test can have one of four outcomes:

* `PASS` -> no errors and any measurements were recorded and validated
* `FAIL` -> the test failed due to a known issue
* `ERROR` -> an unexpected exception was thrown by the test code or underlying lib
* `TIMEOUT` -> Test execution was halted after the timeout_s value was exceeded (currently 3 minutes)

### Test Failures

An STF Test will fail when any of the following conditions are met:
* returning `stf.FAIL` from the test (explict)
* raising an `stf.STFException` or subclass of that exception (other exceptions result in ERROR outcome rather than FAIL)
* not setting a required measurment as defined in the `@stf.measures` decorator
* a requiremed measurement with a validator fails to validate

Note that unexpected errors/exceptions will result in an `ERROR` outcome.

Tests that run more than 3 minutes will be killed and this will result in a `TIMEOUT` outcome.


### Passing a test

A test will pass if it successfully completes with no errors and has made any (optional) declared measurements.

One can explicitly return `stf.FAIL` or `stf.PASS` though the latter will only be valid if the test has no measurements or has made any that it declared

Note that returning stf.PASS will not result in a pass if declared measurements were not made (*more on measurements below).

examples:

```
def test_fn(test, session, **k):
    ... # do some stuff...

    if something.isBad:
        return stf.FAIL

    return stf.PASS
```


explicit pass return value not required:
```
def test_fn(test, session, **k):
    ... # do some stuff...

    if something.isBad:
        return stf.FAIL
```


FAIL due to exception :
```
def test_fn(test, session, **k):
    ... # do some stuff...

    try:
        something():
    except:
        raise stf.STFException("Failed to do 'something'")
```


ERROR due to exception:
```
def test_fn(test, session, **k):
    ... # do some stuff...

    something() # assuming something raises an exception and the exception is not a subclass of STFException
        
```

measurements (more on that below)
```
@stf.measures(stf.Measurement('foo'))
def test_fn(test, session, **k):
    ... # do some stuff...

    test.measurements.foo = something()
```

All the above tests would pass

