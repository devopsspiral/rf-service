import unittest
from rf_runner.arg_parser import ArgParser

example_local_publisher = {"publisher": {
                                "type": "LocalPublisher",
                                "dest": "somecontext"
                            },
                           "fetcher": {},
                           "robotframework": {
                               "include_tags": ["smoke"],
                               "exclude_tags": ["nonsmoke"]
                           }
                           }
example_caddy_publisher = {"publisher": {
                                "type": "CaddyPublisher",
                                "url": "http://rf-service-caddy/uploads"
                            },
                           "fetcher": {}
                           }
example_mixed = {"publisher": {
                                "type": "CaddyPublisher",
                                "url": "http://rf-service-caddy/uploads"
                            },
                 "fetcher": {
                        "type": "ZipFetcher",
                        "url": "https://github.com/devopsspiral/rf-service/archive/master.zip",
                        "path": "rf-service-master/test/resources/testcases"
                       }
                 }


class TestArgParser(unittest.TestCase):

    def test_arg_parser_accepts_json(self):
        ap = ArgParser()
        ap._parse(['test/resources/run1.json'])
        c = ap._get_config()
        self.assertEqual({'type': 'LocalFetcher', 'src': 'testcases'},
                         c.get_fetcher())
        self.assertEqual({'type': 'CaddyPublisher',
                          'url': 'http://127.0.0.1:8080/uploads'},
                         c.get_publisher())
        self.assertEqual('smoke',
                         c.get_rf_settings()['include_tags'][0])

    def test_arg_parser_saves_localpublisher(self):
        ap = ArgParser()
        ap._parse(['--LocalPublisher-dest', 'somecontext'])
        self.assertEqual('somecontext', ap.parameters.LocalPublisher_dest)

    def test_arg_parser_saves_localfetcher(self):
        ap = ArgParser()
        ap._parse(['--LocalFetcher-src', 'somecontext'])
        self.assertEqual('somecontext', ap.parameters.LocalFetcher_src)

    def test_arg_parser_saves_include_tags(self):
        ap = ArgParser()
        ap._parse(['-i', 'smoke', '--include', 'nonsmoke'])
        self.assertEqual(['smoke', 'nonsmoke'], ap.parameters.include_tags)

    def test_arg_parser_saves_exclude_tags(self):
        ap = ArgParser()
        ap._parse(['-e', 'smoke', '--exclude', 'nonsmoke'])
        self.assertEqual(['smoke', 'nonsmoke'], ap.parameters.exclude_tags)

    def test_arg_parser_returns_config(self):
        ap = ArgParser()
        ap._parse(['--LocalPublisher-dest', 'somecontext', '-i', 'smoke', '-e', 'nonsmoke'])
        c = ap._get_config()
        self.assertEqual(example_local_publisher["publisher"], c.get_publisher())
        self.assertEqual(example_local_publisher["robotframework"], c.get_rf_settings())

    def test_arg_parser_returns_config_mixed(self):
        ap = ArgParser()
        ap._parse(['--CaddyPublisher-url', 'http://rf-service-caddy/uploads',
                   '--ZipFetcher-url', 'https://github.com/devopsspiral/rf-service/archive/master.zip',
                   '--ZipFetcher-path', 'rf-service-master/test/resources/testcases'])
        c = ap._get_config()
        self.assertEqual(example_mixed["publisher"], c.get_publisher())
        self.assertEqual(example_mixed["fetcher"], c.get_fetcher())
