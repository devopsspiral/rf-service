import unittest
from rf_runner.config import Config
from rf_runner.publisher_factory import PublisherFactory


example_mixed = {"publisher": {
                                "type": "CaddyPublisher",
                                "url": "http://127.0.0.1:8080/uploads"
                            },
                 "fetcher": {
                        "type": "LocalFetcher",
                        "src": "testcases"
                       }
                 }


class TestConfig(unittest.TestCase):

    def test_config_inits(self):
        c = Config()
        self.assertEqual({}, c.get_fetcher())
        self.assertEqual({}, c.get_publisher())
        self.assertIsNone(c.fetcher_callback)
        self.assertIsNone(c.publisher_callback)

    def test_config_inits_from_file(self):
        c = Config(config_file='test/resources/run1.json')
        self.assertEqual({'type': 'LocalFetcher', 'src': 'testcases'},
                         c.get_fetcher())
        self.assertEqual({'type': 'CaddyPublisher',
                          'url': 'http://127.0.0.1:8080/uploads'},
                         c.get_publisher())

    def test_config_inits_from_dict(self):
        c = Config(data=example_mixed)
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

    def test_config_callback_on_file_config(self):
        c = Config(config_file='test/resources/run1.json')
        called_fetcher = False

        def callback_fetcher():
            nonlocal called_fetcher
            called_fetcher = True

        called_publisher = False

        def callback_publisher():
            nonlocal called_publisher
            called_publisher = True
        c.register_fetcher_callback(callback_fetcher)
        self.assertTrue(called_fetcher)
        c.register_fetcher_callback(callback_publisher)
        self.assertTrue(called_publisher)

    def test_config_callback_on_data_config(self):
        c = Config(data=example_mixed)
        called_fetcher = False

        def callback_fetcher():
            nonlocal called_fetcher
            called_fetcher = True

        called_publisher = False

        def callback_publisher():
            nonlocal called_publisher
            called_publisher = True
        c.register_fetcher_callback(callback_fetcher)
        self.assertTrue(called_fetcher)
        c.register_fetcher_callback(callback_publisher)
        self.assertTrue(called_publisher)

    def test_config_gets_rf_settings(self):
        c = Config(config_file='test/resources/run1.json')
        self.assertEqual('smoke',
                         c.get_rf_settings()['include_tags'][0])

    def test_config_rf_settings_has_defaults(self):
        c = Config(config_file='test/resources/run2.json')
        self.assertIsNone(c.get_rf_settings()['exclude_tags'])
