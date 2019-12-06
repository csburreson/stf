import stf

@stf.test
def run_test(test, session):
    pass

# register decorator accepts version and config file
@stf.register(version='1.0')
class Simple(stf.MainboardTest):
    '''
    Docstring is included in test results as the
    test description
    '''
    TESTS = [run_test]


if __name__ == '__main__':
    stf.run()



