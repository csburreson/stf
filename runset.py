import stf
import sys
import os
import argparse

if __name__ == '__main__':
    args = stf.util.misc.get_runset_args()
    setName = args.set_name

    #if not args.run and not setName:
    if not setName:
        print("No set name provided, choose one of:")
        files = os.listdir(stf.config.get_path('setconfig'))
        configs = [f[:-5] for f in files if f.endswith('.json')]
        print("  " + "\n  ".join(configs))  
        raise SystemExit

    if setName.endswith('.json'):
        setName = setName[:-5]

    stf.config.setIcebootOpts(host=args.iceboot_host, port=args.iceboot_port, debug=args.iceboot_debug)
    print(f"Starting test run with iceboot settings:\n\thost={args.iceboot_host}\n\tport={args.iceboot_port}\n\tdebug={args.iceboot_debug}")
    #stf.run_set(setName, list_tests=args.tests, list_overrides=args.configs,
    stf.run_set(setName, device_host=args.iceboot_host, device_port=args.iceboot_port)
