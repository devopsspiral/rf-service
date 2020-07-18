from robot.api import TestSuiteBuilder


class Executor(object):

    def __init__(self, context=None):
        self.context = context

    def execute(self, paths=None, include_tags=None, exclude_tags=None):
        if not paths:
            suite = TestSuiteBuilder().build(self.context)
        else:
            suite = TestSuiteBuilder().build(paths)
        suite.configure(include_tags=include_tags, exclude_tags=exclude_tags)
        return suite.run()
