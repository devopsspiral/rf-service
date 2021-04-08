import logging
import requests
from datetime import datetime
from robot.api import ResultWriter
from rf_runner.exceptions import NotOverriddenException
from azure.storage.blob import BlobServiceClient, ContentSettings, __version__

logger = logging.getLogger("publisher")
logger.setLevel(logging.INFO)


class AbstractPublisher(object):
    def __init__(self, data):
        self.publish_target = None
        self._load_meta(data)

    def _load_meta(self, data):
        """Load parameters from json structure"""
        raise NotOverriddenException

    def get_standard_reportname(self):
        return datetime.now().strftime('%d-%m-%yT%H%M%S-%f')

    def publish(self, result):
        self._publish(result)
        logger.info(f'Test report generated using {self.__class__.__name__}: {self.publish_target or ""}')

    def _publish(self, result):
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
        self.context = data['dest']

    def _publish(self, result):
        reportname = self.get_standard_reportname()
        if self.context:
            reportname = f'{self.context}{reportname}'
        ResultWriter(result).write_results(report=f'{reportname}.html',
                                                  log=None)

    def _jsonify(self):
        return {'dest': self.context}

    @staticmethod
    def meta():
        return {'dest': 'str'}


class CaddyPublisher(AbstractPublisher):
    """ Publish reports to Caddy server with upload plugin

        https://hub.docker.com/r/jumanjiman/caddy
    """

    def _load_meta(self, data):
        self.url = data['url']

    def _publish(self, result):
        reportname = self.get_standard_reportname()
        ResultWriter(result).write_results(report=f'/tmp/{reportname}.html',
                                           log=None)
        with open(f'/tmp/{reportname}.html', 'rb') as data:
            requests.put(f'{self.url}/{reportname}.html', data=data)

    def _jsonify(self):
        return {'url': self.url}

    @staticmethod
    def meta():
        return {'url': 'str'}


class AzureBlobPublisher(AbstractPublisher):
    """ Publish reports to Azure Blob storage on $web container
    """

    def _load_meta(self, data):
        self.connection_string = data['connection_string']
        self.path = data.get('path')
        self.prefix = data.get('prefix')
        self.blob_url = data.get('blob_url')

    def _publish(self, result):
        reportname = self.get_standard_reportname()
        upload_file_path = f'/tmp/{reportname}.html'
        ResultWriter(result).write_results(report=upload_file_path,
                                           log=None)
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        container_name = "$web"
        target_blob = f"{self.path or ''}{self.prefix or ''}{reportname}.html"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=target_blob)

        static_html_content_settings = ContentSettings(content_type='text/html')
        with open(upload_file_path, "rb") as data:
            blob_client.upload_blob(data, content_settings=static_html_content_settings)
        self.publish_target = f'{self.blob_url or ""}/{target_blob}'

    def _jsonify(self):
        return {'connection_string': self.connection_string,
                'path': self.path,
                'prefix': self.prefix,
                'blob_url': self.blob_url}

    @staticmethod
    def meta():
        return {'connection_string': 'str',
                'path': 'str',
                'prefix': 'str',
                'blob_url': 'str'}
