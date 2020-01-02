# Framework Configuration

## Default Config

The framwork includes a default configuration which should not be modified (at least not committed to the respository)

For local development, create a file called `stfconfig.local.json` in the workspace home (STF_HOME)

This file will be ignored by git so you needn't worry about committing it.

Feel free to `cp stfconfig.json stfconfig.local.json` and edit away.

Note that the file MUST be valid JSON with the exception of comments being allowed, like other STF-JSON configuration files.

***see STF_HOME/stfconfig.json***
```
{
    /*
    output settings for the output of test runs
        console output by default provides slightly more information than pass/fail
        json output is our preferred default for the time being
        in the future, we may wish to add a "database" output option
    */
    "output": {
        "console": {
            "enabled": true
        },
        "json": {
            "enabled": true,
            "filename": "{metadata[test_group]}{metadata[test_name]}-v{metadata[test_version]}-degg-{dut_id}.json"
        },
        // not implemented
        "database": null,
        // not implemented
        "quiet": "disabled"
    },
    /*
    paths contain directories and filenames to relevant resources
        paths can reference other paths within this configuration section
        or any part of this configuration object by using "config.<section>.<key>[... .<subkey>]]"
    */
    "paths": {
        // this defaults to stf workspace directory and should probably remain unset
        "stf_home": null,
        "data": "{stf_home}/data",
        "tests": "{stf_home}/tests",
        "testconfig": "{data}/testconfig",
        "setconfig": "{data}/setconfig",
        // full path here ** note: cannot mix relative config refs and absolute
        "fwfile": "{config.paths.data}/fw_{config.iceboot.fw_version}.rbf",
        // local path passed to iceboot session for flashing fw
        "fwfile_remote": "degg_fw_v{config.iceboot.fw_version}.rbf",
        //"fwfile_path": "{data}/{fwfile_pattern}",
        "json_output": "{stf_home}/results/{config.output.json.filename}"
    },
    /*
    iceboot options include the current FW version and normal iceboot
        connection string business
    */
    "iceboot": {
        "fw_version": "0xb0",
        "host": "localhost",
        "port": 5012,
        "debug": false
    },
          
    /*   
    currently loading "all.json" for single tests... this section will
    change with future development, but should contain information about how to
    access our devices

    it's possible this would be paired with a device "manifest" file or maybe
    db connection/query information
    */
    "device": {
        "type": "jsonfile", // jsonfile, or db conn string eventually ?
        "source": "all.json" 
    }
    
}   
```

## Test Config files "config" section

THe test config `iceboot` section will no longer have any effect; the framework will now completely ignore testconfig `config.iceboot`.

It's possible other `config` sections might be desirable in tests (i.e. timeouts based on config? and perhaps overridable in setconfigs`) but for now
but currently the framework does not make use of any testconfig `config` section params.
