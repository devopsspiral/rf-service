import os
import mock
import requests
import unittest
from datetime import datetime
from rf_runner.fetcher import LocalFetcher
from rf_runner.publisher import AbstractPublisher, LocalPublisher, \
                                CaddyPublisher, AzureBlobPublisher
from rf_runner.publisher_factory import PublisherFactory
from rf_runner.executor import Executor
from rf_runner.exceptions import NotOverriddenException
from azure.storage.blob import BlobClient


def mock_func_from_connection_string(connection_string):
    return TestBlobServiceClient()


class TestBlobServiceClient(object):

    def get_blob_client(*args, **kwargs):
        return TestBlobServiceClient()

    def upload_blob(*args, **kwargs):
        pass


class TestPublisher(unittest.TestCase):

    def test_abstract_publisher_inits(self):
        self.assertRaises(NotOverriddenException, AbstractPublisher, {})

    def test_publisher_factory_creates_localpublisher(self):
        data = {'type': 'LocalPublisher', 'dest': 'somecontext'}
        f = PublisherFactory.get(data)
        self.assertIsNone(f.publish_target)
        self.assertTrue(isinstance(f, LocalPublisher))

    def test_publisher_factory_creates_caddypublisher(self):
        data = {'type': 'CaddyPublisher', 'url': 'http://someurl'}
        f = PublisherFactory.get(data)
        self.assertTrue(isinstance(f, CaddyPublisher))

    def test_publisher_factory_creates_azureblobpublisher(self):
        data = {'type': 'AzureBlobPublisher', 'connection_string': 'http://someurl'}
        f = PublisherFactory.get(data)
        self.assertTrue(isinstance(f, AzureBlobPublisher))

    def test_local_publisher_inits(self):
        p = LocalPublisher({'dest': 'results'})
        self.assertEqual('results', p.context)

    def test_local_publisher_jsonify(self):
        p = LocalPublisher({'dest': 'results'})
        self.assertEqual({'type': 'LocalPublisher', 'dest': 'results'}, p.jsonify())

    def test_caddypublisher_jsonify(self):
        p = CaddyPublisher({'url': 'http://127.0.0.1:8080/uploads'})
        self.assertEqual({'type': 'CaddyPublisher',
                          'url': 'http://127.0.0.1:8080/uploads'}, p.jsonify())

    def test_azureblobpublisher_jsonify(self):
        p = AzureBlobPublisher({'connection_string': 'http://someurl',
                                'path': 'path/to/container/',
                                'prefix': 'super_test_prefix-',
                                'blob_url': 'http://blob-url'})
        self.assertEqual({'type': 'AzureBlobPublisher',
                          'connection_string': 'http://someurl',
                          'path': 'path/to/container/',
                          'prefix': 'super_test_prefix-',
                          'blob_url': 'http://blob-url'}, p.jsonify())

    def test_localpublisher_publishes_from_result(self):
        with LocalFetcher({'src': 'test/resources/testcases'}) as f:
            f.update()
            e = Executor(f.get_context())
            p = LocalPublisher({'dest': f.get_context()})
            result = e.execute()
            stats = result.suite.statistics
            self.assertEqual(stats.critical.total, 2)
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
        with LocalFetcher({'src': 'test/resources/testcases'}) as f:
            f.update()
            e = Executor(f.get_context())
            p = CaddyPublisher({'url': url})
            result = e.execute()
            stats = result.suite.statistics
            self.assertEqual(stats.critical.total, 2)
            p.publish(result)
            now = datetime.now().strftime('%d-%m-%yT%H%M')
            self.assertTrue(mock_put.call_args.args[0]
                                    .startswith(f'{url}/{now}'))
            self.assertTrue(mock_put.call_args.kwargs['data'].name
                                    .startswith(f'/tmp/{now}'))

    @mock.patch('azure.storage.blob.BlobServiceClient.from_connection_string')
    def test_azureblobpublisher_publishes_from_result(self, mock_from_connection_string):
        connection_string = "https://azure.connection.string"
        path = "path/to/container/"
        prefix = "super_test_prefix-"
        mock_from_connection_string.side_effect = mock_func_from_connection_string
        with mock.patch.object(TestBlobServiceClient, 'get_blob_client', return_value=TestBlobServiceClient()) as mock_get_blob_client:
            with LocalFetcher({'src': 'test/resources/testcases'}) as f:
                f.update()
                e = Executor(f.get_context())
                p = AzureBlobPublisher({'connection_string': connection_string,
                                        'path': path,
                                        'prefix': prefix})
                result = e.execute()
                stats = result.suite.statistics
                self.assertEqual(stats.critical.total, 2)
                p.publish(result)
                self.assertIsNotNone(p.publish_target)
                mock_from_connection_string.assert_called_with(connection_string)
                now = datetime.now().strftime('%d-%m-%y')
                self.assertEqual(mock_get_blob_client.call_args.kwargs['container'], '$web')
                self.assertTrue(mock_get_blob_client.call_args.kwargs['blob']
                                .startswith(f'path/to/container/super_test_prefix-{now}'))
                self.assertTrue(mock_get_blob_client.call_args.kwargs['blob']
                                .endswith('.html'))

    @mock.patch('azure.storage.blob.BlobServiceClient.from_connection_string')
    def test_azureblobpublisher_publishes_without_path_and_prefix(self, mock_from_connection_string):
        connection_string = "https://azure.connection.string"
        mock_from_connection_string.side_effect = mock_func_from_connection_string
        with mock.patch.object(TestBlobServiceClient, 'get_blob_client', return_value=TestBlobServiceClient()) as mock_get_blob_client:
            with LocalFetcher({'src': 'test/resources/testcases'}) as f:
                f.update()
                e = Executor(f.get_context())
                p = AzureBlobPublisher({'connection_string': connection_string})
                result = e.execute()
                stats = result.suite.statistics
                self.assertEqual(stats.critical.total, 2)
                p.publish(result)
                mock_from_connection_string.assert_called_with(connection_string)
                now = datetime.now().strftime('%d-%m-%y')
                self.assertEqual(mock_get_blob_client.call_args.kwargs['container'], '$web')
                self.assertTrue(mock_get_blob_client.call_args.kwargs['blob']
                                .startswith(f'{now}'))
                self.assertTrue(mock_get_blob_client.call_args.kwargs['blob']
                                .endswith('.html'))
