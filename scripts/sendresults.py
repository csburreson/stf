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
    global args
    url = '{}://{}/{}/data/testsets/'.format(args.scheme, args.host, args.basepath)
    print('Sending to: {}'.format(url))
    data = {'resultDoc': d, 'timeslug': timeslug,
        'user': args.user, 'password': args.password}
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
    ap.add_argument('--user', help='REQUIRED')
    ap.add_argument('--password', help='REQUIRED')
    ap.add_argument('--host', nargs='?', default='hercules.icecube.wisc.edu', help='Defaults to hercules')
    ap.add_argument('--scheme', nargs='?', default='https', help='(dev) defaults to https')
    ap.add_argument('--basepath', '-b',  default='prodcal', help='(dev) location of flask app on server')
    args = ap.parse_args()
    
    for fname in args.files:
        main(fname)
        time.sleep(0.3)
