import unittest
from rf_runner.fetcher_factory import FetcherFactory


class TestFetcherFactory(unittest.TestCase):

    def test_fetcher_factory_inits(self):
        ff = FetcherFactory()

    def test_fetcher_factory_gets_meta(self):
        ff = FetcherFactory()
        expected = {
                        'ZipFetcher': {
                            'url': 'string',
                            'path': 'string'
                        },
                        'LocalFetcher': {
                            'src': 'string'
                        }
                    }
        self.assertEqual(expected, ff.get_meta())
