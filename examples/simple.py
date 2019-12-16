import stf
import numpy as np

print( "HERE")
@stf.measures(
    stf.M('foo').with_dimensions(),
    stf.M('bar').with_dimensions()
)
def run_test(test, session):
    test.measurements.foo = [1,2,3]
    test.measurements.bar = np.array([1,2,3]).tolist()

    #x = test.measurements.bar.tolist()

    stf.debug('{}'.format(len(x)))

    return stf.PASS

# register decorator accepts version and config file
stf.register(
    version='1.0',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
