import json
import mock
import unittest
from rf_runner.executor import Executor
from robot.api import ResultWriter
from rf_runner.fetcher import LocalFetcher
from rf_runner.runner import Runner


class TestRunner(unittest.TestCase):
    @mock.patch('rf_runner.publisher.CaddyPublisher.publish')
    @mock.patch('rf_runner.fetcher.LocalFetcher.update')
    def test_runner_runs1(self, fetcher_update, publisher_publish):
        with open('test/resources/run1.json') as json_file:
            data = json.load(json_file)
            r = Runner(data)
            r.run()
            fetcher_update.assert_called_once()
            publisher_publish.assert_called_once()

    @mock.patch('rf_runner.publisher.LocalPublisher.publish')
    @mock.patch('rf_runner.fetcher.ZipFetcher.update')
    def test_runner_runs2(self, fetcher_update, publisher_publish):
        with open('test/resources/run2.json') as json_file:
            data = json.load(json_file)
            r = Runner(data)
            r.run()
            fetcher_update.assert_called_once()
            publisher_publish.assert_called_once()
