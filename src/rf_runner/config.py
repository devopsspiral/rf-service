import json


class Config(object):

    def __init__(self, config_file=None):
        self.fetcher = {}
        self.publisher = {}
        self.fetcher_callback = None
        self.publisher_callback = None
        self.config_file = config_file
        if config_file:
            with open(config_file) as json_file:
                data = json.load(json_file)
                self.load_fetcher(data.get('fetcher'))
                self.load_publisher(data.get('publisher'))

    def register_fetcher_callback(self, callback):
        self.fetcher_callback = callback
        if self.config_file:
            callback()

    def register_publisher_callback(self, callback):
        self.publisher_callback = callback
        if self.config_file:
            callback()

    def load_publisher(self, config):
        self.publisher = config
        if self.publisher_callback:
            self.publisher_callback()

    def get_publisher(self):
        return self.publisher

    def load_fetcher(self, config):
        self.fetcher = config
        if self.fetcher_callback:
            self.fetcher_callback()

    def get_fetcher(self):
        return self.fetcher
