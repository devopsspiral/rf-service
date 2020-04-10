import json
import mock
import unittest
from rf_runner.executor import Executor
from robot.api import ResultWriter
from rf_runner.fetcher import LocalFetcher
from rf_runner.runner import Runner
from rf_runner.config import Config


class TestRunner(unittest.TestCase):

    @mock.patch('rf_runner.fetcher.LocalFetcher.update')
    def test_runner_inits(self, fetcher_update):
        c = Config()
        r = Runner(c)
        self.assertEqual(None, r.fetcher)
        self.assertEqual(None, r.publisher)
        fetcher_update.assert_not_called()
        p_config = {'type': 'LocalPublisher', 'src': 'testcases'}
        c.load_publisher(p_config)
        f_config = {'type': 'LocalFetcher', 'src': 'testcases'}
        c.load_fetcher(f_config)
        fetcher_update.assert_called_once()
        self.assertEqual(f_config, r.config.get_fetcher())
        self.assertEqual(p_config, r.config.get_publisher())
        r.cleanup()

    @mock.patch('rf_runner.fetcher.LocalFetcher.update')
    @mock.patch('rf_runner.fetcher.LocalFetcher.create_context')
    def test_runner_gets_fetcher_and_publisher(self, create_context, fetcher_update):
        c = Config()
        r = Runner(c)
        p_config = {'type': 'LocalPublisher', 'dest': 'testcases'}
        c.load_publisher(p_config)
        f_config = {'type': 'LocalFetcher', 'src': 'testcases'}
        c.load_fetcher(f_config)
        self.assertEqual({'src': 'string'}, r.fetcher.meta())
        self.assertEqual({'dest': 'string'}, r.publisher.meta())
        create_context.assert_called_once()
        fetcher_update.assert_called_once()

    def test_runner_discovers_tests(self):
        c = Config('test/resources/run_k8s.json')
        r = Runner(c)
        tests = r.discover_tests()
        self.assertEqual('KubeLibrary-master', tests[0]['name'])
        self.assertEqual('Testcases', tests[0]['children'][0]['name'])
        self.assertEqual('System Smoke', tests[0]['children'][0]['children'][0]['name'])
        self.assertEqual('Kubernetes has correct version', tests[0]['children'][0]['children'][0]['children'][0]['name'])
        r.cleanup()

    def test_runner_discovers_tests_when_not_initialized(self):
        c = Config()
        r = Runner(c)
        self.assertEqual([], r.discover_tests())

    @mock.patch('rf_runner.publisher.CaddyPublisher.publish')
    @mock.patch('rf_runner.fetcher.LocalFetcher.update')
    def test_runner_runs1(self, fetcher_update, publisher_publish):
        c = Config('test/resources/run1.json')
        r = Runner(c)
        r.run()
        fetcher_update.assert_called_once()
        publisher_publish.assert_called_once()
        r.cleanup()

    @mock.patch('rf_runner.publisher.LocalPublisher.publish')
    @mock.patch('rf_runner.fetcher.ZipFetcher.update')
    def test_runner_runs2(self, fetcher_update, publisher_publish):
        c = Config('test/resources/run2.json')
        r = Runner(c)
        r.run()
        fetcher_update.assert_called_once()
        publisher_publish.assert_called_once()
        r.cleanup()
