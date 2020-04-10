import unittest
from rf_runner.publisher_factory import PublisherFactory


class TestPublisherFactory(unittest.TestCase):

    def test_publisher_factory_inits(self):
        pf = PublisherFactory()

    def test_publisher_factory_gets_meta(self):
        pf = PublisherFactory()
        expected = {
                        'CaddyPublisher': {
                            'url': 'string'
                        },
                        'LocalPublisher': {
                            'dest': 'string'
                        }
                    }
        self.assertEqual(expected, pf.get_meta())