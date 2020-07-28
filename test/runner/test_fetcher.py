import mock
import os
import unittest
import shutil
from rf_runner.fetcher import AbstractFetcher, LocalFetcher, ZipFetcher
from rf_runner.fetcher_factory import FetcherFactory

lf_config = {'src': 'testcases'}
zf_config = {'url': 'https://github.com/devopsspiral/rf-service/archive/octopus_support.zip'}
zfp_config = {'url': 'https://github.com/devopsspiral/rf-service/archive/octopus_support.zip',
              'path': 'rf-service-octopus_support/test/resources/testcases'}


class TestFetcher(unittest.TestCase):

    def test_abstract_fetcher_inits(self):
        f = AbstractFetcher()
        self.assertFalse(os.path.exists(f.context))
        self.assertTrue(f.context.startswith('/tmp/rf-runner/'))
        self.assertFalse(f.context.endswith('rf-runner/'))
        another = AbstractFetcher()
        self.assertNotEqual(f.context, another.context)

    def test_abstract_fetcher_gets_context(self):
        f = AbstractFetcher()
        self.assertTrue(f.context, f.get_context())

    @mock.patch('rf_runner.fetcher.AbstractFetcher.fetch')
    @mock.patch('rf_runner.fetcher.AbstractFetcher.clean')
    def test_abstract_fetcher_update_runs_clean_and_fetch(self, mock_clean, mock_fetch):
        f = AbstractFetcher()
        f.update()
        mock_fetch.assert_called_once()
        mock_clean.assert_called_once()

    def test_abstract_fetcher_creates_and_cleans_context(self):
        with AbstractFetcher() as f:
            self.assertTrue(os.path.exists(f.context))
        self.assertFalse(os.path.exists(f.context))

    def test_fetcher_factory_creates_localfetcher(self):
        data = {'type': 'LocalFetcher', 'src': 'testcases'}
        f = FetcherFactory.get(data)
        self.assertTrue(isinstance(f, LocalFetcher))
        self.assertEqual('testcases', f.src)

    def test_fetcher_factory_creates_zipfetcher(self):
        data = {'type': 'ZipFetcher', 'url': 'http://someurl'}
        f = FetcherFactory.get(data)
        self.assertTrue(isinstance(f, ZipFetcher))
        self.assertEqual('http://someurl', f.url)
        data = {'type': 'ZipFetcher', 'url': 'http://someurl', 'path': 'somepath'}
        f = FetcherFactory.get(data)
        self.assertEqual('http://someurl', f.url)
        self.assertEqual('somepath', f.path)

    def test_local_fetcher_inits(self):
        f = LocalFetcher(lf_config)
        self.assertFalse(os.path.exists(f.context))
        self.assertTrue(f.context.startswith('/tmp/rf-runner/'))

    def test_local_fetcher_gets_files(self):
        with LocalFetcher(lf_config) as f:
            f.fetch()
            self.assertEqual(1, len(os.listdir(f.get_context())))
        self.assertFalse(os.path.exists(f.context))

    def test_local_fetcher_cleans_context(self):
        with LocalFetcher(lf_config) as f:
            f.fetch()
            self.assertEqual(1, len(os.listdir(f.get_context())))
            f.clean()
            self.assertEqual(0, len(os.listdir(f.get_context())))

    def test_local_fetcher_removes_before_fetch(self):
        with LocalFetcher(lf_config) as f:
            f.update()
            file_path = os.path.join(f.get_context(),
                                     os.listdir(f.get_context())[0])
            shutil.copy(file_path, file_path+'_bu')
            f.update()
            self.assertEqual(1, len(os.listdir(f.get_context())))

    def test_zip_fetcher_inits(self):
        f = ZipFetcher(zf_config)
        self.assertFalse(os.path.exists(f.context))
        self.assertTrue(f.context.startswith('/tmp/rf-runner/'))

    def test_zip_fetcher_gets_all_files(self):
        with ZipFetcher(zf_config) as f:
            f.fetch()
            self.assertEqual('rf-service-octopus_support', os.listdir(f.get_context())[0])
        self.assertFalse(os.path.exists(f.context))

    def test_zip_fetcher_gets_specific_dir(self):
        with ZipFetcher(zfp_config) as f:
            f.fetch()
            existing_files = []
            for r, _, files in os.walk(f.get_context()):
                for filename in files:
                    existing_files.append(os.path.join(r, filename))
            self.assertEqual(2, len(existing_files))
