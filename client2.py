import Test

class MainboardTestPhases(Test.MainboardTest):
    @Test.measures(Test.M('bootup_status').equals('OK'))
    def bootup(test, session):
        test.measurements.bootup_status = session.cmd('boot')
      
    @Test.measures(Test.M('do_flash').equals('OK'))
    def flash(test, session):
        test.measurements.do_flash = session.cmd('flash')

    @Test.measures(Test.M('funkItUp').equals('OK'))
    def funkItUp(test, session):
        test.measurements.funkItUp = session.cmd('funkItUp')

    def stopTest(test, session):
        # do something with session...
        # you can halt text execution:
        return Test.STOP

    @Test.test
    def cause_an_error(test, session):
        # just throw an error for demo purposes
        x = 1 / 0  # DivideByZeroError

    @Test.test
    def long_test(test, session):
        test.logger.info('long_test... sleeping')
        import time
        time.sleep(5)


class SuperMainboardTest(Test.MainboardTest):
    '''
    This is a docstring comment

    This will show up in the TEST RESULTS!
    '''
    VERSION = '1'

    TESTS = [
      MainboardTestPhases.bootup,
      MainboardTestPhases.flash,
      # this test throws an error
      MainboardTestPhases.funkItUp,
      MainboardTestPhases.flash,
    ]

class DuperMainboardTest(Test.MainboardTest):
    '''
    This is a docstring comment
    '''
    DESC = 'Duper MB mbtest -- with failure'
    VERSION = '1'

    TESTS = [
      MainboardTestPhases.bootup,
      MainboardTestPhases.flash,
      MainboardTestPhases.funkItUp,
      #lambda t: t.logger.info('CHECKPOINT'),
      #Test.CHECKPOINT(),
      MainboardTestPhases.flash,
    ]


class CheckpointExampleTest(Test.MainboardTest):
    '''
    This is a docstring comment
    '''
    DESC = 'SUPER mbtest'
    VERSION = '1.0'

    TESTS = [
      MainboardTestPhases.bootup,
      MainboardTestPhases.flash,
      #lambda t, s: t.logger.info('CHECKPOINT'),
      MainboardTestPhases.cause_an_error,
      Test.CHECKPOINT(),
      MainboardTestPhases.long_test, # this test will not run
    ]

Test.run() 
