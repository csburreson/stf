import stf

print( "HERE")
def run_test(test, session, **kw):
    return stf.PASS

# register decorator accepts version and config file
stf.register(
    version='1.0',
    run=run_test,
)


if __name__ == '__main__':
    stf.run()
