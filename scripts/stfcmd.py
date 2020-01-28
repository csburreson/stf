import cmd
import stf
import argparse
from scripts.outcomes import runset_report, runset_summary

def show_tests():
    f = stf.util.files.globFiles(stf.config.get_path('testconfig'), pattern='*.py'), 
    #stf.debug(f'{f}')
    tests = [stf.util.files.getNameFromPath(t) for t in f]
    print('Available tests: ' + '\n'.join(tests))

def complete_show_tests():
    # return list_tests()
    td = stf.config.get_path('tests')
    return [stf.util.files.getNameFromPath(x) for x in stf.util.files.globFiles(td, pattern='*.py')]

def show_testsets():
    pass

def show_results(rf):
    pass


def parse(line):
    x = line.split()
    return len(x), x

class STFShell(cmd.Cmd):
    def do_show(self, cmd, *args):
        try:
            fn = globals()[f'show_{cmd}']
            #eval(f'fn = show_{cmd}')
            fn()
        except NameError:
            print(f'Invalid argument for "{cmd}": {args}')

    def complete_show(self, text, line, ibeg, iend):

        argc, args = parse(line)
        print(f'text="{text}", line="{line}", argc="{argc}", args={args}')

        showables = [c[5:] for c in globals().keys() if c.startswith('show_')]
        if argc == 1:
            return showables

        if argc == 2:
            if text in showables or args[-1] in showables:
                return eval(f'complete_show_{text}()')
                try: 
                    return eval(f'complete_show_{text}()')
                except:
                    return []
            return [x for x in showables if x[5:].startswith(text)]

        if argc == 3:
                try: 
                    return eval(f'complete_show_{args[1]}("{text}")')
                except:
                    return []
        return []

    def do_report(self, text, line, i0, i1):
        pass
        

    def do_EOF(self, line):
        return True

def cli():
    # parse args: cmd, arg, --opts
    p = argparse.ArgumentParser()

    p.add_argument('cmd', choices=(
        'report', 'summary', 'shell'
    ))
    p.add_argument('arg', nargs='?')
    p.add_argument('--out',
        default='console',
        choices=('console', 'consolebrief', 'html', 'csv', 'json'),
    )

    args = p.parse_args()

    # cmds that don't take args:
    if args.cmd == 'shell':
        shell()

    if not args.arg:
        p.error(f'"{args.cmd}" requires an argument')

    # cmds that take args
    if args.cmd == 'report':
        runset_report(args.arg)

    if args.cmd == 'summary':
        runset_summary(args.arg, out=args.out)


    
def shell():
    STFShell().cmdloop(intro=f'STF Shell v{stf.__version__} (in development)')


if __name__ == '__main__':
    #shell()
    cli()

