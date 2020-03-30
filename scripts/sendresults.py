import json
import re
import argparse
from datetime import datetime
import glob
from pathlib import Path
import requests
import time

DEBUG = False

def send_report(d, timeslug=None):
    url = 'https://hercules.icecube.wisc.edu/prodcal/data/testsets'
    data = {'resultDoc': d, 'timeslug': timeslug}
    response = requests.post(url, json=data)

    if DEBUG:
        print(response.status_code)
    print(response.json())


def main(filename):
    p = Path(filename)
    if p.exists() and p.is_file():
        load(filename)

    if p.exists() and p.is_dir():
        files = p.glob('**/*.json')
        for f in files:
            try:
                load(f)
            except Exception as e:
                print("Exception: {}".format(e))


def get_testgroup_id(path):
    ptn = '\d\d\d\d\.\d\d\.\d\d\_\d\d\d\d\d\d'
    for p in Path(path).parts:
        if re.match(ptn, p):
            return p
    

def load(filename):
    print("Loading {}".format(filename))
    try:
        with open(filename, 'r') as f:
            resultDoc = json.load(f)
    except:
        with filename.open() as f:
            resultDoc = json.load(f)


    timeslug = get_testgroup_id(filename)
    if resultDoc['metadata'].get('test_group_id', False) == False:
        resultDoc['metadata']['test_group_id'] = timeslug

    send_report(resultDoc, timeslug)

if __name__ == '__main__':
    import os
    ap = argparse.ArgumentParser(description='Ingest STF Results Files')
    ap.add_argument('files', nargs='+', default='.')
    args = ap.parse_args()
    
    for fname in args.files:
        main(fname)
        time.sleep(0.3)
