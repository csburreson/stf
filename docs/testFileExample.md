
# Test File Examples

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

## Other Examples

The STF [examples](../examples) directory contains simple example concepts.


The STF [tests](../tests) directory is full of functional test examples.

