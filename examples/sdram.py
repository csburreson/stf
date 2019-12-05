import teflon
from fpga_reg import *
import numpy as np
#from dpram import *

PAGES_TO_TEST = 100

def fill_dpram(self, *args):
    pass
def fpga_write(*args):
    pass
sleep = 1
def fpga_read(*args):
    teflon.dbg('reading...')
    global sleep
    import time
    time.sleep(0.5)
    sleep += 1
    return 3 - sleep

def sdram_write(test, session, dpram_num=0):
    import time
    time.sleep(1)
    
    # write to sdram
    fpga_write(session, 'sdram_task', 1 << (5 + 2*dpram_num))

    # wait for task to complete
    while fpga_read(session, 'sdram_task') != 0:
        pass


@teflon.options(timeout_s=10)
def sdram_read(session, dpram_num):
    # read from sdram
    fpga_write(session, 'sdram_task', 1 << (4 + 2*dpram_num))

    # wait for task to complete
    while fpga_read(session, 'sdram_task') != 0:
        pass


def set_sdram_adr(session, adr, dpram_num):
    fpga_write(session, 'sdram_adr_low[%d]' % dpram_num, adr & 0xffff)
    fpga_write(session, 'sdram_adr_high[%d]' % dpram_num, adr >> 16)


@teflon.options(timeout_s=10)
@teflon.test
def run_test(test, session, dpram_nums):
    for dpram_num in [0, 1]:
        print('\n---Testing SDRAM lane %d---\n' % dpram_num)
        # write to sdram
        sdram_write(session, 'dpram_select', dpram_num)

        #htf.util.timeouts.take_at_most_n_seconds(2, sdram_write, session, 'dpram_select', dpram_num)
        
        sdram_write(session, dpram_num)

        #htf.loop_until_timeout_or_not_none(5, 
        fpga_write(session, 'dpram_select', dpram_num)
        set_sdram_adr(session, 0, dpram_num)

        # write ramp pattern to dpram
        pattern = np.arange(1, 2049, dtype=np.int16)
        fill_dpram(session, pattern)

        print('Testing ramp pattern to page 0...')


        # clear dpram
        fill_dpram(session, np.zeros(2048, dtype=np.int16))
        # check that dpram was cleared
        check_read_values(np.zeros(2048, dtype=np.int16),
                          fpga_read(session, 0, 2048), dpram_num)

        # read sdram
        sdram_read(session, dpram_num)

        # check the read values
        check_read_values(pattern, fpga_read(session, 0, 2048),
                          dpram_num)

        # try writing to address 1 and reading back from 0 again
        print('Checking write to adr 1:')
        set_sdram_adr(session, 1, dpram_num)

        sdram_write(session, dpram_num)

        set_sdram_adr(session, 0, dpram_num)

        sdram_read(session, dpram_num)

        read_vals = fpga_read(session, 0, 2048)
        expected_pat = np.empty_like(pattern)
        expected_pat[:4] = pattern[:4]
        expected_pat[4:] = pattern[0:-4]
        check_read_values(expected_pat, read_vals,
                          dpram_num)

        # write random patterns to PAGES_TO_TEST pages in sequence;
        # read them back and make sure they match
        print('Checking writes to first %d pages...' % PAGES_TO_TEST)
        rand_patterns = []
        for i in range(PAGES_TO_TEST):
            rand_patterns.append(fill_dpram_rand(session))
            set_sdram_adr(session, i*512, dpram_num)
            sdram_write(session, dpram_num)

            if i != 0 and i % 10 == 0:
                print('Wrote to page %d' % i)

        all_match = True
        for i in range(PAGES_TO_TEST):
            print('Checking page %d:' % i)
            set_sdram_adr(session, i*512, dpram_num)
            sdram_read(session, dpram_num)
            all_match &= check_read_values(rand_patterns[i],
                                           fpga_read(session, 0, 2048),
                                           dpram_num)

        
        if not all_match:
            teflon.debug('Failure! Mismatch found.')
            # fail and continue
            return teflon.FAIL
        else:
            teflon.debug('Success! All read values are as expected.')
            # no need for explicit continue here, but why not?
            return teflon.CONTINUE


# register decorator accepts version and config file
#   
@teflon.register(version='1.0', config_file='data/testconfig/sdram.json')
class SDRAMTest(teflon.MainboardTest):
    '''
    Docstring is included in test results as the test description
    '''
    TESTS = [run_test]


# this allows us to easily define tests
if __name__ == '__main__':
    teflon.run()
