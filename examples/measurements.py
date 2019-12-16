import stf


# these tests will PASS
@stf.measures(stf.Measurement('foo'))
def pass_measure(test, session):
    test.measurements.foo = 42 


@stf.measures(stf.Measurement('foo'))
def pass_measure_none(test, session):
    test.measurements.foo = None

@stf.measures(
    stf.Measurement('foo'),
    stf.Measurement('bar'),
    stf.Measurement('car').equals(42)
)
def pass_measure_many(test, session):
    test.measurements.foo = 'foo'
    test.measurements.bar = 'bar'
    test.measurements.car = 42

@stf.measures(stf.Measurement('foo'))
def fail_nomeasure(test, session):
    pass

@stf.measures(stf.Measurement('foo'))
def fail_after_measure(test, session):
    test.measurements.foo = False
    return stf.FAIL


for f in [pass_measure, pass_measure_none, pass_measure_many,
    fail_nomeasure, fail_after_measure]:

    stf.register(
        version='1.0',
        run=f,
        test_name=f.func.__name__,
        config_file=stf.NOCONFIG,
    )

# Uses equalsParam and expectedValues; see CONFIG_FILE for more
CONFIG_FILE = 'data/testconfig/measurements.json'

@stf.measures(stf.Measurement('foo').equalsParam('fooVal'))
def pass_foo_bar_literal(test, session, **kw):
    test.measurements.foo = 'bar'  # fooVal is set to 'bar' in config file

# declared measurements "args" and "expectedValues" can use the same names
# the next two tests are equivalent:
@stf.measures(stf.Measurement('fooVal').equalsParam('fooVal'))
def pass_foo_bar_arg(test, session, fooVal, **kw):
    test.logger.info('arg: {}'.format(fooVal))
    test.measurements.fooVal = 'bar'  


# in this test, the names is changed to reflect what different fooVals mean
@stf.measures(stf.Measurement('fooValMeasurment').equalsParam('fooVal'))
def pass_foo_bar_arg2(test, session, fooVal=None, **kw):  
    test.logger.info('this argument is not used by the test: {}'.format(fooVal))
    test.measurements.fooValMeasurment = 'bar'

# this test will fail due to a bad measurement validation
@stf.measures(stf.Measurement('fooVal').equalsParam('fooVal'))
def fail_foo_bar(test, session, fooVal=None, **kw):
    # fooVal the argument is set to "NAR!" in the config, but the expectedValue
    # fooVal is set to "Bar". 
    test.measurements.fooVal = fooVal 


for f in [ pass_foo_bar_literal,
           pass_foo_bar_arg,
           pass_foo_bar_arg2,
           fail_foo_bar]:
    stf.register(
        version='1.0',
        run=f,
        test_name=f.func.__name__,
        config_file=CONFIG_FILE,
    )

if __name__ == '__main__':
    stf.run()
