import os
from base import TestBase
from imw_clustcr import datasets, read_cdr3, metarepertoire

# set this dir with os path
this_dir = os.path.dirname(os.path.abspath(__file__))

class InputTest(TestBase):

    def test_testing_data(self):
        datasets.test_cdr3()
        datasets.test_epitopes()

    def test_vdj(self):
        datasets.vdjdb_alpha()
        datasets.vdjdb_beta()
        datasets.vdjdb_paired()
        datasets.vdjdb_alpha(epitopes=True)
        datasets.vdjdb_beta(epitopes=True)
        datasets.vdjdb_paired(epitopes=True)

    def test_read_immune(self):
        read_cdr3(os.path.join(this_dir, 'input/immuneaccess/HIP05763.tsv'), data_format='immuneaccess')

    def test_metarepertoire(self):
        metarepertoire(os.path.join(this_dir, 'input/immuneaccess/'), data_format='immuneaccess', out_format='CDR3', n_sequences=10 ** 3)

