# Troubleshooting
This document discusses STF issues (never!) and troubleshooting.

## Configuration Verification
First the obvious stuff ...

Before undertaking a test issue diagnostic session, verify test test system
configuration.

### STF Installation
Verify 
[system requirements](system-requirements.md), and 
STF is 
[installed](installation.md) correctly.

### Current Software

Verify latest software

#### STF
Using a git client, ensure the `STF_HOME` workspace is running the latest
software, on the default (`master`) branch, and any pending edits are
understood. `STF_HOME` indicates the root of the STF workspace:


Change to the root of the STF workspace, indicated by `STF_HOME`:
```
$ cd `STF_HOME`
```

Look at `git status` output. Verify the correct branch (typically `master`) and
any pending edits are understood:
```
$ git status
```

Ensure latest STF software:
```
$ git pull
```
STF uses git submodules, so also ensure all submodules are
[updated](git-submodule-hints.md).

#### Iceboot
On the test target mainboard, ensure the latest
[release](https://wiki.icecube.wisc.edu/index.php/Upgrade_STM32_Releases) of
Iceboot is installed.

#### FPGA Firmware
The STF framework automatically loads the latest
[release](https://wiki.icecube.wisc.edu/index.php/Upgrade_DEgg_FPGA_Releases)
of FPGA firmware. Hooray.

### Verify Target IceBoot Network Access
Ensure access to the test target (Device Under Test or DUT) main board Iceboot
session.

First verify the test target is specified in the `STF_HOME`/stfconfig.local.json` `iceboot` stanza:
```
    "iceboot": {
        //"port": 5011,
        "port": 5012,
        //"host": "localhost"
        //"host": "haltstf"
        "host": "drts"
    }
```

Verify network access to the test target IP. For the above _iceboot_ stanza:
```
$ ping drts
PING drts.icecube.wisc.edu (10.134.32.51) 56(84) bytes of data.
64 bytes from drts.icecube.wisc.edu (10.134.32.51): icmp_seq=1 ttl=64 time=0.034 ms
64 bytes from drts.icecube.wisc.edu (10.134.32.51): icmp_seq=2 ttl=64 time=0.057 ms
64 bytes from drts.icecube.wisc.edu (10.134.32.51): icmp_seq=3 ttl=64 time=0.050 ms
```

Verify network access to the test target Iceboot with the telnet utility. For the above _iceboot_ stanza:
```
$ telnet drts 5012
Trying ::1...
telnet: connect to address ::1: Connection refused
Trying 10.134.32.51...
Connected to 
Escape character is '^]'.


> ^]quit

telnet> quit

```
This shows a successful connection to a mainboard running the Iceboot
application.  All is well.

Alternatively the DRTS-3 and DRTS-4 host `haltstf` is running the _bootloader_
application, which then runs Iceboot:

```
$ telnet haltstf 5012
Last login: Tue Mar 31 19:28:40 2020 from pub1.icecube.wisc.edu
[deggtest@hydrometeor ~]$
[deggtest@hydrometeor ~]$ telnet haltstf 5012
Trying 10.134.32.52...
Connected to haltstf.
Escape character is '^]'.


Unknown command:

IceCube STM32 Bootloader
boot: Boot the main application
update: Update the main application
#
```
This shows a successful connection to a mainboard running the _bootloader_
application, which may then invoke Iceboot. All is well.

## Diagnostic Techniques
### Enable Debugging Output
Set the `STF_DEBUG` environment to enable framework verbose debugging output:
```
$ STF_DEBUG=1 python3 tests/MyTest.py
```

Enable increasing levels of test verbosity with the test or runset _-v_ or _-vv_ or _-vvv_ runtime flags. These will reveal any information and error messages from the individual tests:
```
$ python3 tests/MyTest.py -vvv
```

Note that all of `STF_DEBUG` and verbosity flags may be combined for maximum
output:
```
$ STF_DEBUG=1 python3 tests/MyTest.py -vvv
```

The STF framework intercepts all standard Python _print_ statements, so these
can not be added for debugging. Instead there are 2 alternatives:

First, extra diagnostic output may be added to the test file with the line:
```
  test.logger.info('my diagnostic message')
```
  and displayed with the test _-v_ runtime flag. Remember to remove these for
  temporary debugging.

Second, temporary print output may be added with the _stf.PRINT()_ statement.
These do not need _-v_ runtime flags, and must be removed when done:
```
  stf._PRINT('my temporary diagnostic message')
```

### Inspect Test Results
Review the associated test results file in the `STF_HOME/results/`
subdirectory tree. This is often the newest file in the tree:
```
$ find results -type f | xargs ls -rlt | tail
-rw------- 1 jweber jweber 11913 Mar 11 13:56 results/HALT/2020.03.11_184024/degg-c42570cc1482/ScalerScan-base-channel-1-v1.0_degg-c42570cc1482.json
-rw------- 1 jweber jweber 11915 Mar 11 13:57 results/HALT/2020.03.11_184024/degg-c42570cc1482/ScalerScan-dacIncr20-channel-0-v1.0_degg-c42570cc1482.json
-rw------- 1 jweber jweber 11915 Mar 11 13:57 results/HALT/2020.03.11_184024/degg-c42570cc1482/ScalerScan-dacIncr20-channel-1-v1.0_degg-c42570cc1482.json
-rw------- 1 jweber jweber 14044 Mar 11 13:57 results/HALT/2020.03.11_184024/degg-c42570cc1482/TempCompare-base-v1.0_degg-c42570cc1482.json

# less results/HALT/2020.03.11_184024/degg-c42570cc1482/TempCompare-base-v1.0_degg-c42570cc1482.json
```
Verify input arguments, expectedValues are as expected. Review all messages
generated by the test. Any exceptions encountered by the test are here, along
with calling stack backtraces.

### STF Support Resources
Finally, the following are available for STF Support:

Colin Burreson: email
[Colin.Burreson@icecube.wisc.edu](mailto:Colin.Burreson@icecube.wisc.edu),
Slack: `@csburreson`

Jeff Weber: email
[Jeff.Weber@icecube.wisc.edu](mailto:Jeff.Weber@icecube.wisc.edu),
Slack: `@jwweber`

## Common Issues

### Python2
STF only supports Python3. If encountering unexplainable parser syntax errors,
verify the file does not have any
[Python2-only code](https://python-future.org/compatible_idioms.html). Failure
to parse Python3's [f-strings](https://realpython.com/python-f-strings/) is an
immediate indication of this issue.

### Can't Load Modules
In addition to any system level Python module search directories, the
`PYTHONPATH` environment should contain the `STF_HOME` root of the stf
installion workspace. e.g:
```
$ cd stf
$ export PYTHONPATH=`pwd`
```

### Forgotten Content in stfconfig.local.json
Any overrides in stfconfig.local.json always override framework defaults. `git
status` will not show any status of stfconfig.local.json.

### Timeouts
By default STF assumes any test which lasts over 3 minutes is hung, kills the
test, and reports the outcome as a failure. If the test _really_ does run for
more than 3 minutess, either
1. Consider updating the test to require less time to perform the same
   functionality. The Upgrade project will accumulate thousands of hours of
   test time. Every minute saved helps.
2. Instruct STF to override the default timeout for the given test with a
   decorator expressing the timeout in seconds. The decorator may be placed
   alongside the test measurement decorators:
```
@stf.options(timeout_s=240)
```

### Exceptions
The STF console session will report if a test terminates abnormally with an
exception. To debug, [inspect test results](#inspect-test-results) for the
exception and the calling stack backtrace.

Known exceptions:

* [Timeouts](#timeouts) above may cause an exception.
* Operating system errors, such as disk full, no file access permissions, etc.
* `STFRefuseToRun` for no Internet access to [timeserver)[#timeserver).

### Communications Issues

#### Cannot Access Target IceBoot
Verify via
[Verify Target IceBoot Network Access](#verify-target-iceboot-network-access)
above.

#### Timeserver
STF requires a test platform which has a local clock synchronized to an
Internet time server, by default. If not true, STF will raise a 
`STFRefuseToRun` exception. There will be a message in the test 
[results](#inspect-test-results).

First, verify the timeserver is available from any browsers: 
http://worldtimeapi.org/api/timezone/Zulu . The output should be similar to
```
{"week_number":14,"utc_offset":"+00:00","utc_datetime":"2020-04-02T12:58:37.835551+00:00","unixtime":1585832317,"timezone":"Zulu","raw_offset":0,"dst_until":null,"dst_offset":0,"dst_from":null,"dst":false,"day_of_year":93,"day_of_week":4,"datetime":"2020-04-02T12:58:37.835551+00:00","client_ip":"96.37.95.237","abbreviation":"UTC"}
```
and not contain any errors. There have been occasions where this server
responds with an HTTP error. This leads to a `STFRefuseToRun` exception in the
test output.


Use `curl` to verify network access to the Internet timeserver from the STF
test host shell:
```
$ curl  http://worldtimeapi.org/api/timezone/Zulu
{"week_number":14,"utc_offset":"+00:00","utc_datetime":"2020-04-01T22:26:30.376552+00:00","unixtime":1585779990,"timezone":"Zulu","raw_offset":0,"dst_until":null,"dst_offset":0,"dst_from":null,"dst":false,"day_of_year":92,"day_of_week":3,"datetime":"2020-04-01T22:26:30.376552+00:00","client_ip":"128.104.141.56","abbreviation":"UTC"}[jweber@haltstf stf]$

```
should not show an error.

#### Too Many Hops
Test network configurations with multiple hops have produced non repeatable
results and failures. This can occur if the network access to the test target
IceBoot traverses multiple hops, e.g:
* 1 hop from remote test host to pub.icecube.wisc.edu, another hop to test
  target interface and port. Access via ssh
[tunnels](https://wiki.icecube.wisc.edu/index.php/DRTS#Communicating_with_the_the_DEgg_Board)
has proven unstable at times.
* 1 hop from remote test host to pub.icecube.wisc.edu, another hop to a
[serial redirect](https://wiki.icecube.wisc.edu/index.php/DRTS#Communicating_with_the_the_DEgg_Board).

Each hop adds serial buffering to the network path, which may compromise
communications. If these issues are suspected, reduce the number of hops in the
network path. Running STF on a host with locally connected mainboard test targets has
zero hops and eliminates the problem completely. If a locally connected test
target is not possible, use a network switch or router, and avoid SSH tunnels.

If the communications path must use ICM/serial communications, it is
recommended to first validate communications using the test target ethernet
interface, before using the ICM/serial interface.


