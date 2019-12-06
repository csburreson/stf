import stf

@stf.register(
    version='1.0'
)
class TimeoutExample(stf.MainboardTest):
    '''
    This example test set demonstrates a failure due to a test timeout
    '''
    # options with timeout_s=n allows tests to be halted after n seconds
    @stf.options(timeout_s=2)
    def bar(test, session):
        '''this test will fail with TIMEOUT'''
        import time
        time.sleep(4)

    # hoping to eliminate the need for this by just "discovering" all the
    # functions in a class
    TESTS = [bar]


if __name__ == '__main__':
    stf.run()
