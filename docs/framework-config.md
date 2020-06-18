# Framework Configuration

This document details the configuration files used by STF.

All STF configuration files use the [JSON](https://www.json.org/json-en.html)
format. As an STF extension, C and C++ style comments are allowed (and
encouraged) to make the files more readable. JSON syntax errors may lead to
unexpected and indeterminate test results.
When modifiying a JSON file, it is good practice to parse check the file. This
is often a builtin capability of some editors, browsers. However these may not
tolerate JSON comments. An example of a comment tolerant JSON parse checker is
the `json_verify` tool in the `yajl` package on
RedHat/CentOS/Fedora/ScienticLinux systems:
```
$ json_verify -c <stfconfig.json
JSON is valid
```

## Framework File

The framework includes a default configuration which must not be modified (at least not committed to the respository)

The framework contains output options, path information, iceboot settings and device information. 

For users (test writers), the `iceboot` section will probably be the only interesting part.

The default framework config file is located at `{STF_HOME}/stfconfig.json`
where `STF_HOME` is the top level directory in the STF workspace.

## Local Config (user config)

For local development, users may create a file called `stfconfig.local.json` in (STF_HOME). The file `stfconfig.local.json` may be used to locally overide portions or all of `{STF_HOME}/stfconfig.json`.

This file will be ignored by git so you needn't worry about committing it

This file is optional, and if present is automatically loaded by the framework.

You can copy the entire config:
`cp stfconfig.json stfconfig.local.json` 

Or just create one section to override:
```
{
  "iceboot": {
    "host": "foo",
    "port": 424242
  }
}
```

## Default Config File 
See file [STF_HOME/stfconfig.json](../stfconfig.json).

## Test Config files "config" section

The test config `iceboot` section will no longer have any effect; the framework will now completely ignore testconfig `config.iceboot`.

It's possible other `config` sections might be desirable in tests (i.e. timeouts based on config) and perhaps overridable in setconfigs)
but currently the framework does not make use of any testconfig `config` section params.
