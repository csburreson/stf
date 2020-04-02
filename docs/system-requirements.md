# System Requirements
System requirements for installation of STF.

## Disk
STF locally stores test results, which may exceed 1GB in storage.

## System Clock
The local system clock must be synchronized to an network time protocol (NTP)
server.

## Network Access
Network availability is required to access:

* STF source code repository is frequently updated:
https://github.com/WIPACrepo/stf
* Internet time URL
http://worldtimeapi.org/api/timezone/Zulu
* MongoDB database ingest URL TBD
* Database visualization URL https://hercules.icecube.wisc.edu/prodcal/runset_summary
* Network access to devices under test (DUT), e.g. DEgg mainboard TCP/IP network
  port. DUTs with serial (ICM) access may require serial redirect software.

No inbound network access is required.

## Python
STF requires installation of Python3. The local python3 executable name does
not matter. First, it is recommended to install the Python [pip](https://pypi.org/project/pip/) package manager to install additional Python packages required by STF. On some systems, the Python3 version of pip is `pip3`.

Note: some distbutions provide separate Python2 and Python 3 binaries,
packages; with Python2 being the default. Take care to install Python3
packages.

STF requires the following Python3 packages:
* STF https://github.com/WIPACrepo/stf, which also installs Upgrade STM32Tools
  repository https://github.com/WIPACrepo/STM32Tools as a git submodule.
* openhtf test framework, install `pip[3] install openhtf`
* numpy array computing, install `pip[3] install numpy`
* matplotlib plotting library, install `pip[3] install matplotlib`
* requests, install `pip[3] install requests`


## Software
* local git client

