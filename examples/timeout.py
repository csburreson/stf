import stf

@stf.options(timeout_s=1)
def run_test(test, session):
    import time
    print("HERE")
    test.logger.info('Doing "long running" operation...')
    time.sleep(2)
    test.logger.info('This line is never reached')

    x = 1/0  # neither is this line

stf.register(
    version='1.0',
    name='timeout',
    test_desc='This is a demonstration of a test that times out',
    config_file=stf.NOCONFIG,
    run=run_test
)

if __name__ == '__main__':
    stf.run()
