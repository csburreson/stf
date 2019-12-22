
import stf
import sys

if __name__ == '__main__':
    setName = sys.argv[1]
    if setName.endswith('.json'):
        setName = setName[:-5]
    stf.run_set(setName)
