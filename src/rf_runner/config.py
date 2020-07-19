import json


class Config(object):

    def __init__(self, config_file=None, data=None):
        self.fetcher = {}
        self.publisher = {}
        self.rf_settings = {
            "include_tags": None,
            "exclude_tags": None,
        }
        self.fetcher_callback = None
        self.publisher_callback = None
        self.initialized = False
        _data = None
        if not config_file and not data:
            return
        if config_file:
            with open(config_file) as json_file:
                _data = json.load(json_file)
        elif data:
            _data = data
        self.load_fetcher(_data.get('fetcher'))
        self.load_publisher(_data.get('publisher'))
        for setting in _data.get('robotframework', {}):
            self.rf_settings[setting] = _data['robotframework'][setting]
        self.initialized = True

    def register_fetcher_callback(self, callback):
        self.fetcher_callback = callback
        if self.initialized:
            callback()

    def register_publisher_callback(self, callback):
        self.publisher_callback = callback
        if self.initialized:
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

    def get_rf_settings(self):
        return self.rf_settings
