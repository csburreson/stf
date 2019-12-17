import stf
import numpy as np

@stf.measures(
    stf.M('foo'),
    stf.M('bar').in_range('{foo}', '{bar}', type=int)
)
def run_test(test, session):
    test.measurements.foo = [1,2,3]
    test.measurements.bar = 41

    return stf.PASS

# register decorator accepts version and config file
stf.register(
    version='1.0',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
