import argparse
import json
import sys
from pydoc import locate
from rf_runner.publisher_factory import PublisherFactory
from rf_runner.fetcher_factory import FetcherFactory
from rf_runner.config import Config


class ArgParser(object):

    def __init__(self):
        self.config = {"fetcher": {}, "publisher": {}}
        self.parser = argparse.ArgumentParser(description='RobotFramework service.')
        self.parser.add_argument('config_file', type=str, nargs='?', default=None,
                                 help='JSON config file')
        self.add_arguments_from_meta(PublisherFactory.get_meta())
        self.add_arguments_from_meta(FetcherFactory.get_meta())

    def add_arguments_from_meta(self, p_meta):
        for instance_type, meta in p_meta.items():
            for meta_name in meta:
                self.parser.add_argument(f'--{instance_type}-{meta_name}',
                                         type=locate(meta[meta_name]))

    def _parse(self, args):
        self.parameters = self.parser.parse_args(args)

    def _get_config(self):
        if not self.parameters.config_file:
            self.params_to_dict('Publisher')
            self.params_to_dict('Fetcher')
            return Config(data=self.config)
        return Config(config_file=self.parameters.config_file)

    def get_config(self):
        self._parse(sys.argv[1:])
        return self._get_config()

    def params_to_dict(self, param_group):
        for param_name in dir(self.parameters):
            if param_group in param_name and getattr(self.parameters, param_name):
                param_type = param_name.split('_')[0]
                param = param_name.split('_')[-1]
                self.config.update(
                    {param_group.lower(): {param: getattr(self.parameters, param_name),
                                           'type': param_type}})


