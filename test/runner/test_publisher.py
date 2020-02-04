import os
import mock
import requests
import unittest
from datetime import datetime
from rf_runner.fetcher import LocalFetcher
from rf_runner.publisher import AbstractPublisher, LocalPublisher, \
                                CaddyPublisher, publisher_factory
from rf_runner.executor import Executor


class TestPublisher(unittest.TestCase):

    def test_abstract_publisher_inits(self):
        p = AbstractPublisher('results')
        self.assertEqual('results', p.context)

    def test_publisher_factory_creates_localpublisher(self):
        data = {'type': 'LocalPublisher', 'context': 'somecontext'}
        f = publisher_factory(data)
        self.assertTrue(isinstance(f, LocalPublisher))

    def test_publisher_factory_creates_caddypublisher(self):
        data = {'type': 'CaddyPublisher', 'url': 'http://someurl'}
        f = publisher_factory(data)
        self.assertTrue(isinstance(f, CaddyPublisher))

    def test_local_publisher_inits(self):
        p = LocalPublisher('results')
        self.assertEqual('results', p.context)

    def test_localpublisher_publishes_from_result(self):
        with LocalFetcher('testcases') as f:
            f.update()
            e = Executor(f.get_context())
            p = LocalPublisher(f.get_context())
            result = e.execute()
            stats = result.suite.statistics
            self.assertEqual(stats.critical.total, 1)
            p.publish(result)
            found = False
            for filename in os.listdir(f.get_context()):
                if '.html' in filename:
                    found = True
                    now = datetime.now().strftime('%d-%m-%yT%H%M')
                    self.assertTrue(now in filename)
                self.assertTrue(found)

    @mock.patch('requests.put')
    def test_caddypublisher_publishes_from_result(self, mock_put):
        url = "http://127.0.0.1:8080/uploads"
        with LocalFetcher('testcases') as f:
            f.update()
            e = Executor(f.get_context())
            p = CaddyPublisher(url)
            result = e.execute()
            stats = result.suite.statistics
            self.assertEqual(stats.critical.total, 1)
            p.publish(result)
            now = datetime.now().strftime('%d-%m-%yT%H%M')
            self.assertTrue(mock_put.call_args.args[0]
                                    .startswith(f'{url}/{now}'))
            self.assertTrue(mock_put.call_args.kwargs['data'].name
                                    .startswith(f'/tmp/{now}'))
            

