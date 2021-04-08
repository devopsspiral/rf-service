import json
import mock
import unittest
from rf_runner.executor import Executor
from robot.api import ResultWriter
from rf_runner.fetcher import LocalFetcher
from rf_runner.runner import Runner
from rf_runner.config import Config


class TestRunner(unittest.TestCase):

    @mock.patch('rf_runner.fetcher.LocalFetcher.update')
    def test_runner_inits(self, fetcher_update):
        c = Config()
        r = Runner(c)
        self.assertEqual(None, r.fetcher)
        self.assertEqual(None, r.publisher)
        fetcher_update.assert_not_called()
        p_config = {'type': 'LocalPublisher', 'dest': 'testcases'}
        c.load_publisher(p_config)
        f_config = {'type': 'LocalFetcher', 'src': 'testcases'}
        c.load_fetcher(f_config)
        fetcher_update.assert_called_once()
        self.assertEqual(f_config, r.config.get_fetcher())
        self.assertEqual(p_config, r.config.get_publisher())
        r.cleanup()

    @mock.patch('rf_runner.fetcher.LocalFetcher.update')
    @mock.patch('rf_runner.fetcher.LocalFetcher.create_context')
    def test_runner_gets_fetcher_and_publisher(self, create_context, fetcher_update):
        c = Config()
        r = Runner(c)
        p_config = {'type': 'LocalPublisher', 'dest': 'testcases'}
        c.load_publisher(p_config)
        f_config = {'type': 'LocalFetcher', 'src': 'testcases'}
        c.load_fetcher(f_config)
        self.assertEqual({'src': 'str'}, r.fetcher.meta())
        self.assertEqual({'dest': 'str'}, r.publisher.meta())
        create_context.assert_called_once()
        fetcher_update.assert_called_once()

    def test_runner_discovers_tests(self):
        c = Config('test/resources/run_k8s.json')
        r = Runner(c)
        tests = r.discover_tests()
        self.assertEqual('Rf-Service-Master', tests[0]['name'])
        self.assertEqual('Test', tests[0]['children'][0]['name'])
        self.assertEqual('Resources', tests[0]['children'][0]['children'][0]['name'])
        self.assertEqual('Testcases', tests[0]['children'][0]['children'][0]['children'][0]['name'])
        self.assertEqual('Activate Skynet', tests[0]['children'][0]['children'][0]['children'][0]['children'][0]['name'])
        self.assertEqual('Should Activate Skynet', tests[0]['children'][0]['children'][0]['children'][0]['children'][0]['children'][0]['name'])
        r.cleanup()

    def test_runner_discovers_tests_when_not_initialized(self):
        c = Config()
        r = Runner(c)
        self.assertEqual([], r.discover_tests())

    @mock.patch('rf_runner.executor.Executor.execute')
    @mock.patch('rf_runner.publisher.CaddyPublisher.publish')
    @mock.patch('rf_runner.fetcher.LocalFetcher.update')
    def test_runner_runs1(self, fetcher_update, publisher_publish, executor_execute):
        c = Config('test/resources/run1.json')
        r = Runner(c)
        r.run()
        fetcher_update.assert_called_once()
        executor_execute.assert_called_once_with(include_tags=['smoke'], exclude_tags=['nonsmoke'])
        publisher_publish.assert_called_once()
        r.cleanup()

    @mock.patch('rf_runner.executor.Executor.execute')
    @mock.patch('rf_runner.publisher.LocalPublisher.publish')
    @mock.patch('rf_runner.fetcher.ZipFetcher.update')
    def test_runner_runs2(self, fetcher_update, publisher_publish, executor_execute):
        c = Config('test/resources/run2.json')
        r = Runner(c)
        r.run()
        fetcher_update.assert_called_once()
        executor_execute.assert_called_once_with(include_tags=['smoke'], exclude_tags=None)
        publisher_publish.assert_called_once()
        r.cleanup()

    def test_find_requirements(self):
        c = Config(data={"fetcher": {"type": "LocalFetcher",
                                     "src": "test/resources/testcases"
                                     }
                         })
        r = Runner(c)
        self.assertTrue('requirements.txt' in r.get_requirements())

    def test_find_requirements2(self):
        c = Config(data={"fetcher": {"type": "ZipFetcher",
                                     "url": "https://github.com/devopsspiral/rf-service/archive/master.zip",
                                     "path": "rf-service-master/test/resources/testcases"
                                     }
                         })
        r = Runner(c)
        self.assertTrue('rf-service-master/test/resources/testcases/requirements.txt' in r.get_requirements())

    def test_has_requirements(self):
        c = Config(data={"fetcher": {"type": "LocalFetcher",
                                     "src": "test/resources/testcases"
                                     }
                         })
        r = Runner(c)
        self.assertTrue(r.has_requirements())
        r.cleanup()
        c = Config(data={"fetcher": {"type": "LocalFetcher",
                                     "src": "test"
                                     }
                         })
        r = Runner(c)
        self.assertFalse(r.has_requirements())
        r.cleanup()

    def test_pip_install(self):
        c = Config(data={"fetcher": {"type": "LocalFetcher",
                                     "src": "test/resources/testcases"
                                     }
                         })
        r = Runner(c)
        self.assertTrue('Could not find a version that satisfies' in str(r.pip_install_requirements()))
        r.cleanup()

    @mock.patch('rf_runner.runner.Runner.pip_install_requirements')
    def test_runner_install_dependencies(self, pip_install):
        c = Config(data={"fetcher": {"type": "LocalFetcher",
                                     "src": "test/resources/testcases"
                                     }
                         })
        r = Runner(c)
        pip_install.assert_called_once()
        r.cleanup()
