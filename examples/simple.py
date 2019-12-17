import stf
import numpy as np

@stf.measures(
    stf.M('foo'),
    stf.M('bar')
)
def run_test(test, session):
    test.measurements.foo = [1,2,3]
    test.measurements.bar = np.array([1,2,3])

    return stf.PASS

# register decorator accepts version and config file
stf.register(
    version='1.0',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
