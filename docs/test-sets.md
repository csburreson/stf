
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

## Running a set 

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

Use `python runset.py <setname>` to run a runset.

This will attempt to run all tests in a row and create output files for each
test instance.

Try `python runset.py --help` for a list of  options, including iceboot options


## Runset Args

Args:
* `--host` `--iceboot_host`: the host for the iceboot session
* `--port` `--iceboot_port`: the port for the iceboot session
* `--iceboot_debug` `-D`: enable debugging prints from the iceboot session
* `--prodid` `--mbsnum`: incorporate production id (mb serial number) into output
* `--meta`: add arbitrary key=value metadata 
* `-v[vv]`: verbosity level for OpenHTF logging

Use `python runset.py <setname> --host localhost --port 4444` to run a runset while specifying the host and port for an iceboot session.

You can also add `--prodid` to add a serial number to the device under test (this will appear in the Results metadata).
`--mbsnum` is an alias for this.

One can also add `-D` or `--iceboot_debug` to enable Iceboot Session Debugging strings.

Users can also add metadata with the `--meta` flag.

It works like this:

`python runset.py --meta foo=bar x=y n=42`

Every space-delimited argument after the `--meta` option will be interpreted as `key=value` and included in the results output.

This may be useful for running a runset and including the current temperature or LED light status.

Finally, all unused command line arguments will also be included in the output (though in an unparsed form).


 

