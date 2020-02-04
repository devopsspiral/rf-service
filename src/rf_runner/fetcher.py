import os
import requests
import uuid
import shutil
import zipfile
from .exceptions import NotOverriddenException


class AbstractFetcher(object):
    """Fetcher should get testcases from sources for execution"""

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.context = f'/tmp/rf-runner/{self.id}/'

    def __enter__(self):
        self.create_context()
        return self

    def create_context(self):
        os.makedirs(self.context)

    def update(self):
        """Cleans context and fetch files from source"""
        self.clean()
        self.fetch()

    def clean(self):
        """Cleans context"""
        files = os.listdir(self.context)
        for f in files:
            os.remove(os.path.join(self.context, f))

    def fetch(self):
        """Performs actual fetch of testcases into context folder"""
        raise NotOverriddenException

    def get_context(self):
        """Returns folder with fetched testcases"""
        return self.context

    def __exit__(self, exc_type, exc_value, traceback):
        self.remove()

    def remove(self):
        """Removes all the contect of test context and context itself"""
        shutil.rmtree(self.context)


class LocalFetcher(AbstractFetcher):
    """LocalFetcher takes testcases from local filesystem"""

    def __init__(self, src):
        super().__init__()
        self.src = src

    def fetch(self):
        """Performs actual fetch of testcases into context folder"""
        files = os.listdir(self.src)
        for filename in files:
            file_path = os.path.join(self.src, filename)
            if os.path.isfile(file_path):
                shutil.copy(file_path, self.context)


class ZipFetcher(AbstractFetcher):
    """ZiFetcher takes testcases from zip over http"""

    def __init__(self, url, path=None):
        super().__init__()
        self.url = url
        self.path = path

    def fetch(self):
        """Performs actual fetch of testcases into context folder"""
        zipresp = requests.get(self.url)
        zippath = os.path.join(self.context, 'download.zip')
        open(zippath, 'wb').write(zipresp.content)
        with zipfile.ZipFile(zippath, 'r') as archive:
            if self.path:
                for filename in archive.namelist():
                    if filename.startswith(self.path):
                        archive.extract(filename, self.context)
            else:
                archive.extractall(self.context)
        os.remove(zippath)


def fetcher_factory(fetcher_conf):
    if fetcher_conf['type'] == 'LocalFetcher':
        return LocalFetcher(fetcher_conf['src'])
    elif fetcher_conf['type'] == 'ZipFetcher':
        return ZipFetcher(fetcher_conf['url'], fetcher_conf.get('path', None))
