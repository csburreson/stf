
A runset file which is essentially a manifest of tests and override parameters.

They are stored in `data/setconfig/<set_name>.json` and can be run with the
runset command described later.

The runset file lists test names and defines different test "instances" and overrides.

Instances have an **instance** property which we use as its name and to keep
track of different "flavors" of tests, and overrides for **args** and
**expectedValues** and optionally a **desc** property.

Note that the `instance` value will be used in the filename of the JSON output
document, so please do not use spaces or weird characters.

The runset file must have top-level keyword **tests** which is a dictionary of test
names to lists of instances, as such:

```
{
  "tests": {
     "ADCComms": [{
          "instance": "foo",
          "desc": "a short description of this test instance to be included in the output"
          "args": { ... },
          "expectedValues": { ... },

     }, {
          .... another ADCComms instance here
     }],

     ... more tests here
   }
}
```

To specift a test with its default configuration (a base instance), simply provide an instance
name of **"base"** (with no overrides) or an empty list.

Both **args** and **expectedValues** overrides are optional, but instances
should not be created without one of these (the framework does not enforce this
policy). 


## Base instances

To create a runset with no overrides, simple provide an empty list and the
framework will run the base instance:

```
{
  "tests": {
      "ADCComms": [],
      "Interlock": []
  }
}
```

This will run the two tests `ADCComms` and `Interlock` with default config
settings.


To include the base instance in a list of tests, provide `base` for the
"instance" property. Note that you cannot provide overrides for base instances,
doing so will raise en exception.

```
{
  "tests": {
      "ADCNoiseLevel": [
        { "instance": "base" },
        { 
          "instance": "noisy",
          "expectedValues": { "noise_min": 42, "noise_max": 44 },
        }, {
          "instance": "DACtweak",
          "args": { "dac_val": 42000 }
        }
      ],
      "Interlock": [{"instance": "base"}]
      "SLO_ADC": []
  }
}
```

The above snippet would run 5 tests:

```
ADCNoiseLevel:base
ADCNoiseLevel:noisy
ADCNoiseLevel:DACtweak
Interlock:base
SLO_ADC
```

## Examining runset configs

Run the `runset.py` script with no arguments to see all available runsets:

```
$ python3 runset.py
No set name provided, choose one of:
  brainstorm
  ADCTestGroup.nooverides
  g
  baseinstance.example
  ADCTestGroup.example
  alltests
```

This is simply a listing of `<STF_HOME>/data/setconfig/*.json` with the extension stripped off.

Use `python runset.py <setname> [--tests | --configs]` to get information about runsets.

`--tests` will list out the name of every test instance to be created by the config.


```
$  python3 runset.py --tests baseinstance.example
ADCNoiseLevel:base
ADCNoiseLevel:noisy
ADCNoiseLevel:DACtweak
Interlock:base
SLO_ADC
```

`--configs` will list out the tests instances with configuration overrides applied to the default testconfig.

For example:

```
$  python3 runset.py --configs baseinstance.example
ADCNoiseLevel:base
  args: {'channel': 0, 'dac_val': 31000}
  expv: {'noise_min': 0.5, 'noise_max': 3.0}
ADCNoiseLevel:noisy
  args: {'channel': 0, 'dac_val': 31000}
  expv: {'noise_min': 42, 'noise_max': 44}
ADCNoiseLevel:DACtweak
  args: {'channel': 0, 'dac_val': 42000}
  expv: {'noise_min': 0.5, 'noise_max': 3.0}
Interlock:base
  args: {}
  expv: {'flashInterlockValue': True, 'configInterlockValue': False, 'hvInterlockValue': True, 'lidInterlockValue': True}
SLO_ADC
  args: {'test_context': 'room'}
  expv: {'channel 00 LVS_SLO_IMON_1V1': 0.0, 'channel 01 LVS_SLO_IMON_1V35': 0.0, 'channel 02 LVS_SLO_IMON_1V8': 0.0, 'channel 03 LVS_SLO_IMON_2V5': 0.0, 'channel 04 LVS_SLO_IMON_3V3': 0.0, 'channel 05 +1V8_A': 1.8, 'channel 06 light_sensor_dark_min': 0.0, 'channel 06 light_sensor_dark_max': 0.0, 'channel 07 temperature_room_min': 17.0, 'channel 07 temperature_room_max': 31.0, 'channel 07 temperature_+5': 80.0, 'channel 07 temperature_-20': -20.0, 'channel 07 temperature_-40': -40.0, 'channel 08 SLO_HVS0_VMON': 2000.0, 'channel 09 SLO_HVS0_IMON': 0.0, 'channel 10 SLO_HVS1_VMON': 2000.0, 'channel 11 SLO_HVS1_IMON': 0.0, 'channel 12 +1V1_power_rail_monitor': 1.1, 'channel 13 +1V35_power_rail_monitor': 1.35, 'channel 14 +2V5_power_rail_monitor': 2.5, 'channel 15 +3V3_power_rail_monitor': 3.3, 'voltage_rail_percent': 3.0, 'temperature_soak_percent': 2.0}
```

## Running a set 

Use `python runset.py <setname>` to run a runset.

This will attempt to run all tests in a row and create output files for each
test instance.

Try `python runset.py --help` for a list of  options, including iceboot options

NOTE: the `--quiet` option (an alias for disabling Iceboot debug) will also
suppress HTF `ConsoleOutput`. 
 

