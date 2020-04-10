import os
import mock
import requests
import unittest
from datetime import datetime
from rf_runner.fetcher import LocalFetcher
from rf_runner.publisher import AbstractPublisher, LocalPublisher, \
                                CaddyPublisher
from rf_runner.publisher_factory import PublisherFactory
from rf_runner.executor import Executor
from rf_runner.exceptions import NotOverriddenException


class TestPublisher(unittest.TestCase):

    def test_abstract_publisher_inits(self):
        self.assertRaises(NotOverriddenException, AbstractPublisher, {})

    def test_publisher_factory_creates_localpublisher(self):
        pf = PublisherFactory()
        data = {'type': 'LocalPublisher', 'dest': 'somecontext'}
        f = pf.get(data)
        self.assertTrue(isinstance(f, LocalPublisher))

    def test_publisher_factory_creates_caddypublisher(self):
        pf = PublisherFactory()
        data = {'type': 'CaddyPublisher', 'url': 'http://someurl'}
        f = pf.get(data)
        self.assertTrue(isinstance(f, CaddyPublisher))

    def test_local_publisher_inits(self):
        p = LocalPublisher({'dest': 'results'})
        self.assertEqual('results', p.context)

    def test_local_publisher_jsonify(self):
        p = LocalPublisher({'dest': 'results'})
        self.assertEqual({'type': 'LocalPublisher', 'dest': 'results'}, p.jsonify())

    def test_localpublisher_publishes_from_result(self):
        with LocalFetcher({'src': 'testcases'}) as f:
            f.update()
            e = Executor(f.get_context())
            p = LocalPublisher({'dest': f.get_context()})
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
        with LocalFetcher({'src': 'testcases'}) as f:
            f.update()
            e = Executor(f.get_context())
            p = CaddyPublisher({'url': url})
            result = e.execute()
            stats = result.suite.statistics
            self.assertEqual(stats.critical.total, 1)
            p.publish(result)
            now = datetime.now().strftime('%d-%m-%yT%H%M')
            self.assertTrue(mock_put.call_args.args[0]
                                    .startswith(f'{url}/{now}'))
            self.assertTrue(mock_put.call_args.kwargs['data'].name
                                    .startswith(f'/tmp/{now}'))
