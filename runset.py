import stf
import sys
import os
import argparse

if __name__ == '__main__':
    p = argparse.ArgumentParser(prog='runset')
    p.add_argument('set_name', type=str, nargs='?')
    cmd = p.add_mutually_exclusive_group()
    cmd.add_argument('--run', action='store_true')
    cmd.add_argument('--tests', action='store_true')
    cmd.add_argument('--configs', action='store_true')

    args = p.parse_args()
    setName = args.set_name

    if not args.run and not setName:
        print("No set name provided, choose one of:")
        files = os.listdir(stf.ENV.SETCONFIG_DIR)
        configs = [f[:-5] for f in files if f.endswith('.json')]
        print("  " + "\n  ".join(configs))  
        raise SystemExit

    if args.run:
        if setName.endswith('.json'):
            setName = setName[:-5]
        stf.run_set(setName, list_tests=args.tests, list_overrides=args.configs)
    elif not args.tests and not args.configs:
        #import os
        #if os.path.exists('da
        print(f"Did you want to run {setName}? try:\npython runset.py {setName} --run")
        raise SystemExit

    stf.run_set(setName, list_tests=args.tests, list_overrides=args.configs)
