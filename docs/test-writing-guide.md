
# How To Write an STF test

An stf test is a normal python function which receives special arguments and is run by the framework. 

Minimally, you need a test function, a few lines of boilerplate code, and an optional test config file to write a valid test.


## Test File

A test file must import the stf framework, define a test function, and call `stf.register` on the test.

Calling stf.run() in a test file will allow you to execute the test at the command line.

...please stick to the convention of using `if __name__ == '__main__': \n    stf.run()` as you're writing tests

Here's an example test file:

```
import stf

def test_fn(test, session):
    pass

stf.register(
    version='1.0',
    run=run_test,
    config_file=stf.NOCONFIG
)

# use "python <this-file.py>" to run
# can use "-v[vv]" for different levels of output
if __name__ == '__main__':
    stf.run()
```

This test could be run and would be successful. 

Register also accepts other arguments, like `test_name` and `test_desc` which you may want to fill in.

If not provided, the framework will try to use the name of your testfile (minus the path and extension) as the `test_name` value.

The framework will assume a test config with the same name exists here: `data/testconfig/<test_name>.json`

```
stf.register(
    # version should change if your code changes (required if this test has
    # been used in production). You're in charge of this version as a test writer
    version='1.0',
    # run is required and points to the test function intended to be run
    run=run_test,

    # optional: test_desc is a description of your test which will appear in the output
    test_desc=None,
    # optional: test name is generated from filename if not provided (i.e. 'template' from template.py)
    test_name=None,
    # optional: defaults to std.testclasses.MainboardTest
    test_class=stf.testclasses.MainboardTest,
    # override: use 'config_file' to point to a different location for config
    #   (default is STF_HOME/data/testconfig/<test_name>.json )
    config_file=None
)
```

## Test Function

A minimal test function must accept 2 positional arguments, test and session. 

If your test has arguments (`args`) defined in its config file, they will be available as keyword arguments.

If your test has `expectedValue` paramaters defined in its test config, it will be a required keyword argument; or feel free to use the `**kw` convention.


**test** is the OpenHTF test object and has logging and measurement attributes. 

  use `test.logger.info` (or `.error` or `.warning`) to record log messages in the output
  
  use `test.measurements` for recording measurements (more later).

**session** is an active iceboot session prepared by the framework

  in production, the framework will always send the latest firmware to the mainboard.
  
  while developing tests, one can set the `STF_SKIPFW` flag to skip the uploading of FW.

**kwargs** contains all test config values as defined in the JSON files
    **it also contains the reserved keyword arg** `expectedValues` if (and only if) it is present in your config

### test functions with args and expectedValues:

Test function with arguments:
```
def test_fn(test, session, arg1=None, arg2=None):
    pass
```
```
def test_fn(test, session, **kwargs):
    pass
```


Test function with expected values:
```
def test_fn(test, session, expectedValues):
    pass
```
```
def test_fn(test, session, expectedValues=None):
    pass
```
```
def test_fn(test, session, **kwargs):
    pass
```

Test function with both:
```
def test_fn(test, session, arg1=None, expectedValues=None):
    pass
```
```
def test_fn(test, session, **kwargs):
    pass
```


Test function with expected values
*example tests are located in `STF_HOME/tests/`*

## Test Config

A test config is a JSON file. Your test should use a config for inputting
parameters that may change depending on when and where your test is run.

Config files are used to pass parameters into a test or validate measurements
made during testing or set test configuration options (timeout_s, iceboot
settings)

You *should* use a config file, even if it's blank.

If your test really really does not need a config, use the `stf.NOCONFIG` option.

*NOTE* Currently a config also allows you to override iceboot options, but this feature may go away

example empty file: 
```
{ }
```

or
```
{ 
    "config": {},
    "args": {},
    "expectedValues": {}
}
```
*the default location for test config files is `STF_HOME/data/testconfig/<test-name>.json`*

For now, test writers will provide configuration files to inject arguments or expectedValues into the test.

Arguments can be accessed from the kwargs keyword or mentioned as explicit kw args.

`expectedValues` are put into the **reserved keyword** `expectedValues`


## Passing a test

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

measurements (more on that below)
```
@stf.measures(stf.Measurement('foo'))
def test_fn(test, session, **k):
    ... # do some stuff...

    test.measurements.foo = something()
```

All the above tests would pass

## Measurements

Decorate your test with `@stf.measures(...)` to declare measurements.

The `measures` decorator accepts stf.Measurement (or stf.M for short) objects.

You can record measurements you have declared by using the *test* argument:
`test.measurements.<name-of-declared-measurement>`

Measurements can be validated with the following validators:
  * `.equals(val)` compares recorded measurement against val (usually a literal)
  * `.equalsParam('{expectedValueKey}')` compares the value of an item in the "expectedValue" of the test config JSON file
  * `.in_range(x, y)` valid if measurement if equal to or between x and y
  * `.in_range('{exp_x}', {exp_y})` same, but uses "expectedValue" from testConfig
  * TODO: match?


Example:

```
import stf

@stf.measures(stf.Measurement('xxx').equalsParam('{foo}'))
def run_test(test, session, arg1=None, **kw):
    # see tests/template.json for testconfig
    test.measurements.xxx = 'bar' 

    if arg1 is None:
        test.logger.error('misconfigured arg!')
        return stf.FAIL
    else:
        test.logger.info('Got arg1: {}'.format(arg1))

    # OK if we get here, framework takes care of comparing xxx to bar
    # if they don't match or xxx weren't recorded, the test will fail
```
