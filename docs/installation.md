# STF Installation

## System Requirements
Verify the [system requirements](system-requirements.md) prior to installation.

## Installation

Using a [git](https://git-scm.com/) client, clone a local copy of of the STF
repository. Note the repository uses git submodules, so the clone invocation is
modified:

For ssh authentication:
```
$ git clone --recurse-submodules git@github.com:WIPACrepo/stf.git
```

For https authentication:
```
$ git clone --recurse-submodules https://github.com/WIPACrepo/stf.git
```

If you forget the `--recurse-submodules` or for more notes on git submodules,
there is more [here](git-submodule-hints.md).

Both these clone methods will create a local workspace, named `stf` by default.
This workspace is termed `STF_HOME` in all STF documentation.

Change to the new workspace. STF includes it's own Python modules, so set or
add to the `PYTHONPATH` environment:

```
$ cd stf
$ export PYTHONPATH=`pwd`



