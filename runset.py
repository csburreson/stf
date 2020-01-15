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
    p.add_argument('--iceboot_host', '--host', '-H', type=str, default=None)
    p.add_argument('--iceboot_port', '--port', '-p', type=str, default=None)
    p.add_argument('--iceboot_debug', '-D', action='store_true', default=False)

    args = p.parse_args()
    setName = args.set_name

    if not args.run and not setName:
        print("No set name provided, choose one of:")
        files = os.listdir(stf.config.get_path('setconfig'))
        configs = [f[:-5] for f in files if f.endswith('.json')]
        print("  " + "\n  ".join(configs))  
        raise SystemExit

    if setName.endswith('.json'):
        setName = setName[:-5]
    if not args.tests and not args.configs:
        stf.config.setIcebootOpts(host=args.iceboot_host, port=args.iceboot_port, debug=args.iceboot_debug)
        print(f"Starting test run with iceboot settings:\n\thost={args.iceboot_host}\n\tport={args.iceboot_port}\n\tdebug={args.iceboot_debug}")
    stf.run_set(setName, list_tests=args.tests, list_overrides=args.configs)
