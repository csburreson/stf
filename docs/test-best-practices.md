# Test Best Practices

The following STF test case best practices help test operators understand what a
test does, and why it passes or fails.  Without this understanding, test
operators may need to consult the test author.

Test scripts should support Python-2 (TBD) or Python-3.

The test script file character set should be ASCII or UTF-8.

The test script will be executed as a command line argument to a Python
interpreter. Scripts do not (should not) require execute file permissions. A
Linux first line "shebang" interpreter invocation, e.g. *#!/usr/bin/python* or
*#!/usr/bin/env python* is not necessary, and may be ignored by the STF
framework.

Python script and config file JSON files may be committed to Git with the local
host end of line (EOL) characters, e.g. carriage-return, newline.  Git will
automatically translate the file end of line (EOL) characters to be appropriate
where ever the repository is checked out.

Please use spaces for indention, not TAB characters. Various users and editors
have different expectations for rendering TABs. Further, Python3 does not allow
mixed TABs and spaces.

Each test should should completely configure it's initial state, and not require
or assume initial state from another test. Note the MCU, and FPGA will be reset
between tests.

All test parameters should be defined in the associated test config file. Test
parameters should not be hard coded, nor obtained from other sources, like file
system, environment, network, etc.

Test operators who are not the test author should be able to understand the
function of the test, including what the test does, and why it passes or fails.
Ideally this information comes from runtime messages, and precludes having to
read and interpret the test script.  The *test.measurments()* methods and
*stf.Measurement()* decorators are very useful in this regard, and are
essentially self-documenting.  Generous use of *test.logger.info()*,
*test.logger.error()* and *test.logger.warning()* also help to convey test
messages to the test operator.

Likewise, test operators who are not the test author should be able to
understand test config file pass/fail verification values. Descriptive
expectedValues names are helpful, as are config file comments; see
[data/testconfig/validators.json](https://github.com/WIPACrepo/stf/blob/master/data/testconfig/validators.json) 
for embedded config file comment examples.

