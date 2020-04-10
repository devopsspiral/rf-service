import requests
from datetime import datetime
from robot.api import ResultWriter
from .exceptions import NotOverriddenException


class AbstractPublisher(object):
    def __init__(self, data):
        self._load_meta(data)

    def _load_meta(self, data):
        """Load parameters from json structure"""
        raise NotOverriddenException

    def get_standard_reportname(self):
        return datetime.now().strftime('%d-%m-%yT%H%M%S-%f')

    def publish(self, result):
        """Generate report and place it somewhere"""
        raise NotOverriddenException

    def jsonify(self):
        """Serialize into json"""
        params = {'type': self.__class__.__name__}
        params.update(self._jsonify())
        return params

    def _jsonify(self):
        """Add Publisher specific parameters"""
        raise NotOverriddenException

    @staticmethod
    def meta():
        """Returns parameters needed to initialize Publisher"""
        raise NotOverriddenException


class LocalPublisher(AbstractPublisher):

    def _load_meta(self, data):
        self.context = data.get('dest')

    def publish(self, result):
        reportname = self.get_standard_reportname()
        if self.context:
            reportname = f'{self.context}{reportname}'
        ResultWriter(result).write_results(report=f'{reportname}.html',
                                                  log=None)

    def _jsonify(self):
        return {'dest': self.context}

    @staticmethod
    def meta():
        return {'dest': 'string'}


class CaddyPublisher(AbstractPublisher):
    """ Publish reports to Caddy server with upload plugin

        https://hub.docker.com/r/jumanjiman/caddy
    """

    def _load_meta(self, data):
        self.url = data.get('url')

    def publish(self, result):
        reportname = self.get_standard_reportname()
        ResultWriter(result).write_results(report=f'/tmp/{reportname}.html',
                                           log=None)
        with open(f'/tmp/{reportname}.html', 'rb') as data:
            requests.put(f'{self.url}/{reportname}.html', data=data)

    def _jsonify(self):
        return {'url': self.url}

    @staticmethod
    def meta():
        return {'url': 'string'}
