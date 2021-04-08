import logging
import os
import site
import sys
import subprocess
from robot.api import TestSuiteBuilder
from rf_runner.executor import Executor
from rf_runner.publisher_factory import PublisherFactory
from rf_runner.fetcher_factory import FetcherFactory

logging.basicConfig()
logger = logging.getLogger("runner")
logger.setLevel(logging.INFO)


class Runner(object):
    def __init__(self, config):
        self.config = config
        self.publisher = None
        self.fetcher = None
        self.config.register_fetcher_callback(self.init_fetcher)
        self.config.register_publisher_callback(self.init_publisher)

    def init_fetcher(self):
        if self.config.get_fetcher():
            self.fetcher = FetcherFactory.get(self.config.get_fetcher())
            self.fetcher.create_context()
            self.fetcher.update()
            self.install_dependencies()

    def install_dependencies(self):
        if self.has_requirements():
            logger.info("Installing extra dependencies")
            logger.info(self.pip_install_requirements().decode("utf-8"))

    def get_requirements(self):
        for root, dirs, files in os.walk(self.fetcher.get_context()):
            for file in files:
                if file.endswith("requirements.txt"):
                    return os.path.join(root, file)

    def has_requirements(self):
        if self.get_requirements():
            return True
        return False

    def pip_install_requirements(self):
        pip_cmdline = [sys.executable, '-m', 'pip']
        try:
            # venv
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and (sys.base_prefix != sys.prefix)):
                return subprocess.check_output(pip_cmdline + ['install', '--requirement', str(self.get_requirements())], stderr=subprocess.STDOUT)
            else:
                sys.path.append(site.USER_SITE)
                return subprocess.check_output(pip_cmdline + ['install', '--user', '--requirement', str(self.get_requirements())], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return e.output

    def init_publisher(self):
        if self.config.get_publisher():
            self.publisher = PublisherFactory.get(self.config.get_publisher())

    def discover_tests(self):
        if self.fetcher:
            suites = TestSuiteBuilder().build(self.fetcher.get_context())
            return self.suites_tests(suites)
        else:
            return []

    def suites_tests(self, suites):
        result = []
        if suites.suites:
            for suite in suites.suites:
                result.append({'name': str(suite), 'children': self.suites_tests(suite)})
        else:
            return [{'name': str(test), 'children': []} for test in suites.tests]
        return result

    def run(self):
        e = Executor(self.fetcher.get_context())
        rf_settings = self.config.get_rf_settings()
        self.publisher.publish(e.execute(include_tags=rf_settings['include_tags'],
                                         exclude_tags=rf_settings['exclude_tags']))

    def cleanup(self):
        self.fetcher.remove()
