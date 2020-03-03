import os
DISABLE_COLORS = not os.environ.get('I3TEST_COLOR', True)

def dotdict(d, t='Enum'):
    '''
    pass a dictionary, get a structure allowing JS-like dot notation
    wrapper for "enum"

    >> x = dotdict({'HELLO': 12345})
    >> print x.HELLO
    >> 12345
    '''
    return type(t, (), d)

TerminalColors = {
    'GREEN': '\33[32m',
    'RED': '\33[31m',
    'GRAY': '\33[90m',
    'GOLD': '\33[93m',
    'AQUA': '\33[96m',
    'LPURPLE': '\33[94m',
    'BOLD': '\033[1m',
    # reset will unset the color/style applied
    'RESET': '\x1b[0m'
}

Color = dotdict(TerminalColors)


def termcolor(s, colorname):
    '''
    colorname is either the key for TerminalColors
    or the actual value
    '''
    if DISABLE_COLORS:
        return s

    c = TerminalColors
    try:
        return c[colorname.upper()] + s + Color.RESET
    except:
        pass
    return colorname + s + Color.RESET


def termcolor_cond(string, yesno, yes=Color.GREEN, no=Color.RED):
    return termcolor(string, yes if yesno else no)


def disable_colors():
    global DISABLE_COLORS
    DISABLE_COLORS = True
