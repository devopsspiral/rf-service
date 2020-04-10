import logging
import os
from robot.api import TestSuiteBuilder
from .executor import Executor
from .publisher_factory import PublisherFactory
from .fetcher_factory import FetcherFactory

logger = logging.getLogger("fetcher")


class Runner(object):
    def __init__(self, config):
        self.config = config
        self.publisher = None
        self.fetcher = None
        self.config.register_fetcher_callback(self.init_fetcher)
        self.config.register_publisher_callback(self.init_publisher)

    def init_fetcher(self):
        self.fetcher = FetcherFactory().get(self.config.get_fetcher())
        self.fetcher.create_context()
        self.fetcher.update()

    def init_publisher(self):
        self.publisher = PublisherFactory().get(self.config.get_publisher())

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
        self.publisher.publish(e.execute())

    def cleanup(self):
        self.fetcher.remove()
