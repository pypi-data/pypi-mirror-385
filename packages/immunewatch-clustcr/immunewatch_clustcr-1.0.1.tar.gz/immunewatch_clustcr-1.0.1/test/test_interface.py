import os
from base import TestBase
import imw_clustcr


class InterfaceTest(TestBase):

    def test_version_number(self):
        print('Version number', imw_clustcr.__version__)

    def test_files_included(self):
        pkg_dir = os.path.dirname(imw_clustcr.__file__)
        print(f'Package dir: {pkg_dir}')
        # Check for data files
        data_files = [
            'input/adaptive_imgt_mapping.csv',
            'input/alphabeta_gammadelta_db.tsv',
        ]
        for f in data_files:
            path = os.path.join(pkg_dir, f)
            exists = os.path.exists(path)
            assert exists, f'File {f} not found in package directory'

