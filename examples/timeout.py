import teflon

#@teflon.runnable
@teflon.register(
    version='1.0'
)
class TimeoutExample(teflon.MainboardTest):
    # options with timeout_s=n allows tests to be halted after n seconds
    @teflon.options(timeout_s=2)
    def bar(test, session):
        import time
        time.sleep(4)

    # hoping to eliminate the need for this by just "discovering" all the
    # functions in a class
    TESTS = [bar]

teflon.run()
