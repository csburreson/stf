
# Overview of test files

## Minimal Test Function

A minimal test function accepts 2 positional arguments, test and session, and any number of keyword arguments.

**test** is the OpenHTF test object and has logging and measurement attributes. (more later)

**session** is an active iceboot session.

**kwargs** currently contains all test config values as defined in the JSON files

```
import stf

def test_fn(test, session, **kwargs):
    pass

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

# use "python <this-file.py>" to run
# can use "-v[vv]" for info, warning and error output 
if __name__ == '__main__':
    stf.run()

```

Also required is a config file, even if "empty"

example empty file: 
```
{
  "args": {},
  "expectedValues": {},
}
```

## Passing a test

A test will pass if it successfully completes with no errors and has made any (optional) declared measurements.

One can explicitly return `stf.FAIL` or `stf.PASS` though the latter will only be valid if the test has no measurements or has made any that it declared

Note that returning stf.PASS will not result in a pass if declared measurements were not made.

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

