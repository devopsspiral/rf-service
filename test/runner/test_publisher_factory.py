import unittest
from rf_runner.publisher_factory import PublisherFactory


class TestPublisherFactory(unittest.TestCase):

    def test_publisher_factory_gets_meta(self):
        expected = {
                        'CaddyPublisher': {
                            'url': 'str'
                        },
                        'LocalPublisher': {
                            'dest': 'str'
                        },
                        'AzureBlobPublisher': {
                            'connection_string': 'str',
                            'path': 'str',
                            'prefix': 'str',
                            'blob_url': 'str'}
                    }
        self.assertEqual(expected, PublisherFactory.get_meta())
