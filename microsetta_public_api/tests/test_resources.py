import pandas as pd
import numpy as np
import biom
from pandas.util.testing import assert_series_equal
from qiime2 import Artifact
from q2_types.sample_data import SampleData, AlphaDiversity

from microsetta_public_api.exceptions import ConfigurationError
from microsetta_public_api.utils.testing import TempfileTestCase
from microsetta_public_api.resources import ResourceManager, _parse_q2_data


class TestResourceManagerUpdateAlpha(TempfileTestCase):

    def setUp(self):
        super().setUp()
        self.qza_resource_fp = self.create_tempfile(suffix='.qza').name
        self.qza_resource_fp2 = self.create_tempfile(suffix='.qza').name
        self.qza_resource_fh2 = self.create_tempfile(suffix='.qza')
        self.qza_resource_fh2.close()
        self.qza_resource_dne = self.qza_resource_fh2.name
        self.non_qza_resource_fp = self.create_tempfile(
            suffix='.some_ext').name
        self.test_series = pd.Series({'sample1': 7.15, 'sample2': 9.04},
                                     name='chao1')
        self.test_series2 = pd.Series({'sample1': 7.16, 'sample2': 9.01},
                                      name='faith_pd')
        self.resources = ResourceManager(some_key='some_value')

        imported_artifact = Artifact.import_data(
            "SampleData[AlphaDiversity]", self.test_series
        )
        imported_artifact.save(self.qza_resource_fp)
        self.update_with = {'random-value': 7.24,
                            'alpha_resources': {'chao1': self.qza_resource_fp,
                                                'faith_pd': 9,
                                                },
                            'other': {'dict': {'of': 'things'}},
                            }

    def test_update_alpha_resources(self):

        imported_artifact = Artifact.import_data(
            "SampleData[AlphaDiversity]", self.test_series
        )
        imported_artifact.save(self.qza_resource_fp)
        imported_artifact = Artifact.import_data(
            "SampleData[AlphaDiversity]", self.test_series2
        )
        imported_artifact.save(self.qza_resource_fp2)

        update_with = {'random-value': 7.24,
                       'alpha_resources': {'chao1': self.qza_resource_fp,
                                           'faith_pd': self.qza_resource_fp2,
                                           },
                       'other': {'dict': {'of': 'things'}},
                       }
        self.resources.update(update_with)

        exp = {'some_key': 'some_value',
               'random-value': 7.24,
               'other': {'dict': {'of': 'things'}},
               }

        exp_alpha_resources = {'chao1': self.test_series,
                               'faith_pd': self.test_series2,
                               }
        self.assertIn('alpha_resources', self.resources)
        obs_alpha_resources = self.resources.pop('alpha_resources')
        self.assertDictEqual(self.resources, exp)
        self.assertListEqual(list(obs_alpha_resources.keys()),
                             ['chao1', 'faith_pd'])
        assert_series_equal(obs_alpha_resources['chao1'],
                            exp_alpha_resources['chao1'])
        assert_series_equal(obs_alpha_resources['faith_pd'],
                            exp_alpha_resources['faith_pd'])

    def test_update_alpha_resources_qza_dne(self):
        with self.assertRaisesRegex(ValueError,
                                    'Expected existing path with .qza'):
            self.resources.update(self.update_with)

        with self.assertRaisesRegex(ValueError,
                                    'Expected existing path with .qza'):
            self.update_with['alpha_resources']['faith_pd'] = \
                self.qza_resource_dne
            self.resources.update(self.update_with)

        with self.assertRaisesRegex(ValueError,
                                    'Expected existing path with .qza'):
            self.update_with['faith_pd'] = self.qza_resource_dne
            self.resources.update(alpha_resources=self.update_with)

    def test_update_alpha_resources_path_is_not_qza(self):

        with self.assertRaisesRegex(ValueError,
                                    'Expected existing path with .qza'):
            self.update_with['alpha_resources']['faith_pd'] = \
                self.non_qza_resource_fp
            self.resources.update(self.update_with)

        with self.assertRaisesRegex(ValueError,
                                    'Expected existing path with .qza'):
            self.update_with['faith_pd'] = self.non_qza_resource_fp
            self.resources.update(alpha_resources=self.update_with)

    def test_update_alpha_resources_non_dict(self):
        with self.assertRaisesRegex(ValueError,
                                    "Expected 'alpha_resources' field to "
                                    "contain a dict. Got int"):
            self.update_with['alpha_resources'] = 9
            self.resources.update(self.update_with)

        with self.assertRaisesRegex(ValueError,
                                    "Expected 'alpha_resources' field to "
                                    "contain a dict. Got int"):
            update_with = 9
            self.resources.update(alpha_resources=update_with)


class TestResourceManagerUpdateTables(TempfileTestCase):
    def setUp(self):
        super().setUp()
        self.table = biom.Table(np.array([[0, 1, 2],
                                          [2, 4, 6],
                                          [3, 0, 1]]),
                                ['feature-1', 'feature-2', 'feature-3'],
                                ['sample-1', 'sample-2', 'sample-3'])
        self.taxonomy_df = pd.DataFrame([['feature-1', 'a; b; c', 0.123],
                                         ['feature-2', 'a; b; c; d; e', 0.345],
                                         ['feature-3', 'a; f; g; h', 0.678]],
                                        columns=['Feature ID', 'Taxon',
                                                 'Confidence'])
        self.taxonomy_df.set_index('Feature ID', inplace=True)
        self.table2 = biom.Table([[0, 0.1, 0.2],
                                  [0.2, 0.4, 0.6],
                                  [0.3, 0, 0.1]],
                                 ['feature-1', 'feature-2', 'feature-3'],
                                 ['sample-1', 'sample-2', 'sample-3'])

        self.table_qza = Artifact.import_data(
            "FeatureTable[Frequency]", self.table
        )
        self.taxonomy_qza = Artifact.import_data(
            "FeatureData[Taxonomy]", self.taxonomy_df,
        )
        self.table2_qza = Artifact.import_data(
            "FeatureTable[Frequency]", self.table2
        )

    def test_(self):
        self.fail()


class TestResourceManagerQ2Parse(TempfileTestCase):

    def test_parse_q2_data(self):
        resource_filename = self.create_tempfile(suffix='.qza').name
        test_series = pd.Series({'sample1': 7.15, 'sample2': 9.04},
                                name='chao1')
        imported_artifact = Artifact.import_data(
            "SampleData[AlphaDiversity]", test_series
        )
        imported_artifact.save(resource_filename)

        loaded_artifact = _parse_q2_data(resource_filename,
                                         SampleData[AlphaDiversity])
        assert_series_equal(test_series, loaded_artifact)

    def test_parse_q2_data_wrong_semantic_type(self):
        resource_filename = self.create_tempfile(suffix='.qza').name
        test_series = pd.Series({'feature1': 'k__1', 'feature2': 'k__2'},
                                name='Taxon')
        test_series.index.name = 'Feature ID'
        imported_artifact = Artifact.import_data(
            # the distincion here is that this is not alpha diversity
            "FeatureData[Taxonomy]", test_series
        )
        imported_artifact.save(resource_filename)

        with self.assertRaisesRegex(ConfigurationError,
                                    r"Expected (.*) "
                                    r"'SampleData\[AlphaDiversity\]'. "
                                    r"Received 'FeatureData\[Taxonomy\]'."):
            _parse_q2_data(resource_filename, SampleData[AlphaDiversity])

    def test_parse_q2_data_file_does_not_exist(self):
        resource_file = self.create_tempfile(suffix='.qza')
        resource_filename = resource_file.name
        resource_file.close()

        with self.assertRaisesRegex(ConfigurationError,
                                    r"does not exist"):
            _parse_q2_data(resource_filename, SampleData[AlphaDiversity])
