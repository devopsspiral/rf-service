import unittest
from rf_runner.config import Config
from rf_runner.publisher_factory import PublisherFactory


class TestConfig(unittest.TestCase):

    def test_config_inits(self):
        c = Config()
        self.assertEqual({}, c.get_fetcher())
        self.assertEqual({}, c.get_publisher())
        self.assertIsNone(c.fetcher_callback)
        self.assertIsNone(c.publisher_callback)

    def test_config_inits_from_file(self):
        c = Config('test/resources/run1.json')
        self.assertEqual({'type': 'LocalFetcher', 'src': 'testcases'},
                         c.get_fetcher())
        self.assertEqual({'type': 'CaddyPublisher',
                          'url': 'http://127.0.0.1:8080/uploads'},
                         c.get_publisher())

    def test_config_loads_publisher(self):
        c = Config()
        data = {'type': 'LocalPublisher', 'src': 'somecontext'}
        c.load_publisher(data)
        self.assertEqual(data, c.get_publisher())

    def test_config_loads_fetcher(self):
        c = Config()
        data = {'type': 'LocalFetcher', 'src': 'somecontext'}
        c.load_fetcher(data)
        self.assertEqual(data, c.get_fetcher())

    def test_config_registers_fetcher_callback(self):
        c = Config()
        called = False

        def callback():
            nonlocal called
            called = True
        c.register_fetcher_callback(callback)
        data = {'type': 'LocalFetcher', 'src': 'somecontext'}
        c.load_fetcher(data)
        self.assertTrue(called)

    def test_config_registers_publisher_callback(self):
        c = Config()
        called = False

        def callback():
            nonlocal called
            called = True
        c.register_publisher_callback(callback)
        data = {'type': 'LocalPublisher', 'dest': 'somecontext'}
        c.load_publisher(data)
        self.assertTrue(called)
