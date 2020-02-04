from robot.api import TestSuiteBuilder


class Executor(object):

    def __init__(self, context=None):
        self.context = context

    def execute(self, paths=None):
        if not paths:
            suite = TestSuiteBuilder().build(self.context)
        else:
            suite = TestSuiteBuilder().build(paths)
        return suite.run()
