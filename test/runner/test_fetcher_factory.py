import unittest
from rf_runner.fetcher_factory import FetcherFactory


class TestFetcherFactory(unittest.TestCase):

    # def test_fetcher_factory_inits(self):
    #     ff = FetcherFactory()

    def test_fetcher_factory_gets_meta(self):
        # ff = FetcherFactory()
        expected = {
                        'ZipFetcher': {
                            'url': 'str',
                            'path': 'str'
                        },
                        'LocalFetcher': {
                            'src': 'str'
                        }
                    }
        self.assertEqual(expected, FetcherFactory.get_meta())
