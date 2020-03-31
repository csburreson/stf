# Submitting STF Results

## Submit Script: sendresults.py

The script is located in `STF_HOME/scripts/` 

It does not depend on the STF framework code, and simply submits 
STF results files to a webserver.

It does require the requests library
`pip install requests`
or
`pip3 install requests`

Run it as follows:

`python3 scripts/sendsresults.py <pathToFileOrParentDir> --user icecube --password ******`

Where `pathToFileOrParentDir` can be a directory containing any number of subdirectories which ultimately contain STF Result json files, or a single json file.

The default server location and location are included in the script and can be overridden. For a complete list of options, try `-h`:

```
$ python3 scripts/sendresults.py -h
usage: sendresults.py [-h] [--user USER] [--password PASSWORD] [--host [HOST]]
                      [--scheme [SCHEME]] [--basepath BASEPATH]
                      files [files ...]

Ingest STF Results Files

positional arguments:
  files

optional arguments:
  -h, --help            show this help message and exit
  --user USER           REQUIRED
  --password PASSWORD   REQUIRED
  --host [HOST]         Defaults to hercules
  --scheme [SCHEME]     (dev) defaults to https
  --basepath BASEPATH, -b BASEPATH
                        (dev) location of flask app on server
```

For troubleshooting, please contact @csburreson on slack.

