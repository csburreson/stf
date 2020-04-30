== Units in STF ==

=== Units === 

Units are based on OpenHTF units:

Github link to units file:
[https://github.com/google/openhtf/blob/master/openhtf/util/units.py](OpenHTF Units)


Python inpsection
```
>>> import openhtf
>>> openhtf.units.PICOFARAD
UnitDescriptor(name='picofarad', code='4T', suffix='pF'))
>>> dir(openhtf.units) 
>>> [ ... giant list of all units ]
```

=== Use In Test ===
just call "with_units" on a Measurement object -- no imports required



=== Example ===

example: FEPulserCharge.py
```
import stf
from DEggTest.fepulser import get_pulser_charge, set_dac, set_fepulser_dac, get_baseline_waveform

'''
>>> openhtf.units.PICOFARAD
UnitDescriptor(name='picofarad', code='4T', suffix='pF'))
'''
# chain "with_units" call to Measurement obj; use the unit suffix or name
@stf.measures(
  # with UnitDescriptor "suffix"
  stf.Measurement('meas').with_units('pF').expectRange('{exp_x}', '{exp_y}', type=float),
  # with UnitDescriptor "name"
  stf.Measurement('meas2').with_units('picofarad').expectRange('{exp_x}', '{exp_y}', type=float)
)
def run_test(test, session, channel, dac_val,
              dac_val_fepulser, bins_before_peak, bins_after_peak,
              nsamples=128, n_waveforms=100, **kw): 
```


=== Custom Units ===

It is posisble to create custom units. Please contact the maintainer,
csburreson if you think you need custom units
