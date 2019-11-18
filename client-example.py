# import custom test lib
import Test
import openhtf as htf


# random function which will not be executed as a test
def getSpinStatus():
    import random
    if random.randint(0, 3) != 2:
        return 'OK'
    return 'Error'


class AaronMainboardTest(Test.MainboardTest):
    VERSION = '1.0.0'
    DESC = 'Aaron\'s mainboard test'

    PARAMS = {

    }

   
    @Test.test
    def bop_it(test, session):
        test.logger.info('bop_it')

    @Test.measures('foo')
    def twist_it(test, session):
        '''
        This test will fail if it does not record a value for:
        test.measurements.foo = <something>
        '''
        test.measurements.foo = 'bar'
        test.logger.info('twist_it')

    @Test.measures( Test.Measurement('bar').equals('OK'))
    def spin_it(test, session):
        '''
        This test will randomly fail 
        since getSpinStatus randomly returns either
        "OK" or "Error"
        '''
        test.logger.info('twist_it')
        test.measurements.bar = getSpinStatus()
        
      

    TESTS = [
      bop_it,
      twist_it,
      spin_it
    ]
 

TESTS = [
  AaronMainboardTest.twist_it,
  AaronMainboardTest.spin_it,
  AaronMainboardTest.bop_it
]

x = Test.run()
