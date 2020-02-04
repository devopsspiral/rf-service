import requests
from datetime import datetime
from robot.api import ResultWriter
from .exceptions import NotOverriddenException


class AbstractPublisher(object):
    def __init__(self, context=None):
        self.context = context

    def get_standard_reportname(self):
        return datetime.now().strftime('%d-%m-%yT%H%M%S-%f')

    def publish(self, result):
        """Generate report and place it somewhere"""
        raise NotOverriddenException


class LocalPublisher(AbstractPublisher):
    def publish(self, result):
        reportname = self.get_standard_reportname()
        if self.context:
            reportname = f'{self.context}{reportname}'
        ResultWriter(result).write_results(report=f'{reportname}.html',
                                           log=None)


class CaddyPublisher(AbstractPublisher):
    """ Publish reports to Caddy server with upload plugin

        https://hub.docker.com/r/jumanjiman/caddy
    """

    def __init__(self, url):
        self.url = url

    def publish(self, result):
        reportname = self.get_standard_reportname()
        ResultWriter(result).write_results(report=f'/tmp/{reportname}.html',
                                           log=None)
        with open(f'/tmp/{reportname}.html', 'rb') as data:
            requests.put(f'{self.url}/{reportname}.html', data=data)


def publisher_factory(publisher_conf):
    if publisher_conf['type'] == 'LocalPublisher':
        return LocalPublisher(publisher_conf['context'])
    elif publisher_conf['type'] == 'CaddyPublisher':
        return CaddyPublisher(publisher_conf['url'])
