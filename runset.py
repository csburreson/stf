import stf
import sys
import argparse

if __name__ == '__main__':
    p = argparse.ArgumentParser(prog='runset')
    p.add_argument('set_name', type=str)
    cmd = p.add_mutually_exclusive_group()
    cmd.add_argument('--run', action='store_true')
    cmd.add_argument('--tests', action='store_true')
    cmd.add_argument('--dryrun', action='store_true')

    args = p.parse_args()
    setName = args.set_name

    if args.run:
        if setName.endswith('.json'):
            setName = setName[:-5]
        stf.run_set(setName)
    
    elif args.tests:
        print('todo: list tests')

    elif args.dryrun:
        print('todo: list tests and applied instance overrides')

    else:
        #import os
        #if os.path.exists('da
        print(f"Did you want to run {setName}? try:\npython runset.py {setName} --run")

