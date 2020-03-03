import stf

@stf.options(timeout_s=1)
def timeout_test(test, session):
    print("timeout test print")  # converted to test.logger.info
    import time
    test.logger.info('Doing "long running" operation...')
    time.sleep(2)
    test.logger.info('This line is never reached')

    x = 1/0  # neither is this line

stf.register(
    version='1.0',
    name='timeout_decorated',
    test_desc='This is a demonstration of a test that times out',
    config_file=stf.NOCONFIG,
    run=timeout_test
)

'''
# DEV NOTE: unfortunately this it isn't quite working yet to have
# config['timeout_s']i in a test config file :( 
def timeout_test_configured(test, session):
    print("timeout test print")  # converted to test.logger.info
    import time
    test.logger.info('Doing "long running" operation...')
    time.sleep(2)
    test.logger.info('This line is never reached')

    x = 1/0  # neither is this line

stf.register(
    version='1.0',
    name='timeout',
    test_desc='This is a demonstration of a test that times out',
    # autodiscover config
    run=timeout_test_configured
)
'''

if __name__ == '__main__':
    stf.run()
