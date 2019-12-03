import openhtf as htf
from fake import get_session
import fake


# tests need not be declared within a class; they can be reused
@htf.measures(htf.Measurement(''))
def measure_voltage():
    pass


class DOMTest():
    @htf.measures(htf.Measurement('status').equals('OK', type=str))
    def iceboot(test, dom=None, FAKEresults=None):
        # get data from outside the test (including config)
        #test.logger.info('Running iceboot on device: {}'.format(test.test_record.metadata['device']))

        test.logger.info('Metadata Keys: {}'.format(test.test_record.metadata.keys()))
        results = fake.do_something(test, dom)
        ### can explicitly STOP this test phase...
        #try:
        #    assert results['status'] == 'OK'
        #except AssertionError:
        #    return htf.PhaseResult.STOP

        # but the measurement above includes what we expect the "status" to be
        test.measurements.status = FAKEresults.get('status', None)

        # save arbitrary results with attachments
        #test.attach_from_file('/scratch/some_file.i3file', 
        #    name='{}-data'.format(test.test_record.metadata['subtype']))
        #test.logger.info('Test Attachments {}'.format(test.attachments))

        # add state that persists through tests
        test.state['foo'] = lambda x: [x + '-reticulating', x + '-tickling']
        test.state['bar'] = 'I am a bar'

        #response = test.test_record.metadata['websession'].get('https://hercules.icecube.wisc.edu/moni20_single_dom_detail/133255/19-60/')

        # Example of passing in a "requests" web-session which has authenticated with i3live
        # this is similar to having a 
        ws = test.test_record.metadata['websession']
        if ws:
            test.logger.info('Requesting data from hercules.... ')
            response = ws.get('https://hercules.icecube.wisc.edu/get_livepulse/')
            assert response.status_code == 200
            test.logger.info('Got livepulse ({}): {}'.format(response.status_code, response.content[0:50]))
            test.attach('fooDocument', response.content)
        else:
            test.logger.info('Skipping web session test')
            test.attach('fooDocument', 'skipped')


    #response = session.get(
    #data = response.content

    @htf.measures(htf.Measurement('bar'))
    def run_foo_command(test, cmd_args=[], cmd_kwargs={}):
        test.measurements.bar = 'nar'
        
        test.logger.info("Running cmd with 'foo' with args={} (set in iceboot)".format(', '.join(cmd_args)))
        result = test.state['foo'](*cmd_args)
        test.logger.info("Got result: {}".format(result))

        att = test.get_attachment('fooDocument')
        for name, a in test.attachments.items():
            test.logger.info('Attachment {}: {}'.format(name, a))


        try:
            if test.test_record.metadata['device']['hacks'].get('FAIL_FOO', None) == True:
                x = 10 / 0
        except ZeroDivisionError:
            test.logger.error('Error! Failure in flux capacitance')
            return htf.PhaseResult.STOP
        return htf.PhaseResult.CONTINUE


class VapeTest():
    '''
    The below could be abstracted with a custom decorator that was simpler to use?

    or we could create a class to generates tests for a particular "test class"
    with proper measurements ... like a "DOM" always has "Voltage" and "Current"
    etc....
    '''
    # can only be declared once (belongs in global)
    htf.util.conf.declare('i3LiveInTheHaus', default_value='bar', description='test config')

    @htf.measures(htf.Measurement('taste', units='X'))
    @htf.measures(htf.Measurement('volts', units='V'))
    def coil(test, resist, wattage):
        m = test.measurements
        assert resist > 0
        if resist * wattage < 4.2:
            m.taste = 'good'
        else:
            m.taste = 'burnt'
        test.measurements.volts = resist * wattage
        test.logger.info('{} volts'.format(m.volts))
        

    @htf.measures(htf.Measurement('taste'))
    def puff(test):
        test.measurements.taste = 'delectable'
        test.logger.info('delectable')

    @htf.measures(htf.Measurement('power_time_series')
                  .with_dimensions('ms', 'V', 'A'))
    @htf.measures(htf.Measurement('average_voltage').with_units('V'))
    @htf.measures(htf.Measurement('average_current').with_units('A'))
    @htf.measures(htf.Measurement('resistance').with_units('ohm').in_range(6, 8))
    def run_mod(test):
        import random
        #test.logger.info('Starting Vape test with {}'.format(test.descriptor.metadata['subtype']))
        vci = 0
        vs = 0.0
        cs = 0.0
        for t in range(10):
            resistance = test.test_record.metadata['device']['hacks']['ohms']
            voltage = 10 + 10.0*t
            vs += voltage
            current = voltage / resistance + 0.01 * random.random()
            cs += current
            vci += 1
            dimensions = (t, voltage, current)
            test.measurements['power_time_series'][dimensions] = 0

        # When accessing your multi-dim measurement a DimensionedMeasuredValue
        # is returned.
        dim_measured_value = test.measurements['power_time_series']

        # Let's convert that to a pandas dataframe
        #power_df = dim_measured_value.to_dataframe(columns=['ms', 'V', 'A', 'n/a'])
        #test.logger.info('This is what a dataframe looks like:\n%s', power_df)
        #test.measurements['average_voltage'] = power_df['V'].mean()
        test.measurements['average_voltage'] = float(vs) / float(vci)

        # We can convert the dataframe to a numpy array as well
        #power_array = power_df.as_matrix()
        #test.logger.info('This is the same data in a numpy array:\n%s', power_array)
        #test.measurements['average_current'] = power_array.mean(axis=0)[2]
        test.measurements['average_current'] = float(cs) / float(vci)
        test.measurements['resistance'] = (
            test.measurements['average_voltage'] /
            test.measurements['average_current']
        )

