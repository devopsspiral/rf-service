import unittest
from rf_runner.executor import Executor
from robot.api import ResultWriter
from rf_runner.fetcher import LocalFetcher


class TestExecutor(unittest.TestCase):
    def test_executor_init(self):
        e = Executor('/tmp/rf-runner/')
        self.assertEqual('/tmp/rf-runner/', e.context)

    def test_executor_execute_exact_testcase(self):
        e = Executor()
        result = e.execute('testcases/activate_skynet.robot')
        # ResultWriter(result).write_results(report='skynet.html', log=None)
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.suite.name, 'Activate Skynet')
        test = result.suite.tests[0]
        self.assertEqual(test.name, 'Should Activate Skynet')
        self.assertTrue(test.passed and test.critical)
        stats = result.suite.statistics
        self.assertEqual(stats.critical.total, 1)
        self.assertEqual(stats.critical.failed, 0)

    def test_executor_executes_context(self):
        with LocalFetcher('testcases') as f:
            f.update()
            e = Executor(f.context)
            result = e.execute()
            stats = result.suite.statistics
            self.assertEqual(stats.critical.total, 1)
