'''
demonstrates openhtf framework
'''
import openhtf as htf
import test as T
from openhtf.output.callbacks.json_factory import OutputToJSON as JSON
from openhtf.output.callbacks import console_summary

from openhtf.util import checkpoints

from openhtf.util import conf
from openhtf.output.servers import station_server
from openhtf.output.web_gui import web_launcher
from openhtf.plugs import user_input

def main():
    test_devices()

def get_all_devices():
    '''
    Placeholder for some sort of discovery function for finding hardware
    attached to something somewhere (all quite vague at the moment)
    '''
    return [
        {
            'uuid': '8675309B',
            'type': 'om',
            'subtype': 'D-Egg',
            'name': 'Pedro',
            'hacks': {'status': 'N/A', 'ohms': 42}
        }, {
            'uuid': 'A675309A',
            'type': 'om',
            'subtype': 'mDOM',
            'name': 'Linda',
            'hacks': {'status': 'ERROR', 'ohms': 6.2, 'FAIL_FOO': True}
        }, {
            'uuid': '00000042',
            'type': 'pmt',
            'subtype': 'pDOM',
            'name': 'Harold',
            'hacks': {'status': 'OK', 'ohms': 7}
        }
    ]

def test_devices():
    devices = get_all_devices()

    # for example, pass in cmd_session
    #session = T.get_session()
    session = None

    #def foo(x):
    #    try:

    for device in devices:
        # or could create new session per device here...

        test = htf.Test(
            T.VapeTest.run_mod,
            T.VapeTest.puff,
            T.VapeTest.coil.with_args(resist=0.2, wattage=50),
            checkpoints.checkpoint(),
            T.DOMTest.iceboot.with_args(dom=device, FAKEresults={
                'status': device['hacks']['status']}),
            T.DOMTest.run_foo_command.with_args(cmd_args=['dom'], cmd_kwargs={}),
            #test_name = T.VapeTest.__name__,
            test_version='1.0.2',
            test_description='I am a vape test',
            subtype=device['subtype'],
            type=device['type'],
            websession=session,
            device=device,
            device_config={
                'somesetting': 'somevalue',
            }
        )
        test.configure(name='{}:{}:{}'.format(T.VapeTest.__name__, device['uuid'], device['name']))
        test.add_output_callbacks(JSON('./results/{metadata[type]}.{metadata[subtype]}.{dut_id}.{metadata[test_name]}-v{metadata[test_version]}.json', indent=4, default=str))
        #test.add_output_callbacks(JSON('{dut_id}.{metadata[test_name]}-v{metadata[test_version]}.json', indent=4, inline_attachments=False))
        if False:
            test.add_output_callbacks(console_summary.ConsoleSummary())

        test.execute(test_start=lambda: device['uuid'])

'''
def serve():
    @htf.measures(htf.Measurement('hello_world_measurement'))
    def hello_world(test):
      test.logger.info('Hello World!')
      test.measurements.hello_world_measurement = 'Hello Again!'


      conf.load(station_server_port='4444')
      with station_server.StationServer() as server:
        web_launcher.launch('http://localhost:4444')
        for i in range(5):
          test = htf.Test(hello_world)
          test.add_output_callbacks(server.publish_final_state)
          test.execute(test_start=user_input.prompt_for_test_start())
'''



if __name__ == '__main__':
    main()


