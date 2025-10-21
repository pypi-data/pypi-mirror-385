import os.path
import shutil
from copy import deepcopy
from unittest import TestCase

from eva_sub_cli.metadata import EvaMetadataJson
from eva_sub_cli.validators.validator import Validator, VALIDATION_OUTPUT_DIR
from tests.test_utils import create_mapping_file

expected_validation_results = {
    'shallow_validation': {'requested': False},
    'vcf_check': {
        'input_passed.vcf': {'valid': True, 'error_list': [], 'error_count': 0, 'warning_count': 0,
                             'critical_count': 0, 'critical_list': []}
    },
    'assembly_check': {
        'input_passed.vcf': {'error_list': [], 'mismatch_list': [], 'nb_mismatch': 0, 'nb_error': 0,
                             'match': 247, 'total': 247}
    },
    'sample_check': {
        'overall_differences': False,
        'results_per_analysis': {
            'AA': {
                'difference': False,
                'more_metadata_submitted_files': [],
                'more_per_submitted_files_metadata': {},
                'more_submitted_files_metadata': []
            }
        }
    },
    'evidence_type_check': {
        'AA': {
            'errors': None,
            'evidence_type': 'allele_frequency'
        },
        'report_path': '{resource_dir}/validation_reports/validation_output/other_validations/evidence_type_checker.yml'
    },

    'fasta_check': {
        'input_passed.fa': {'all_insdc': False, 'sequences': [
            {'sequence_name': 1, 'insdc': True, 'sequence_md5': '6681ac2f62509cfc220d78751b8dc524'},
            {'sequence_name': 2, 'insdc': False, 'sequence_md5': 'd2b3f22704d944f92a6bc45b6603ea2d'}
        ]},
    },
    'metadata_check': {
        'json_errors': [
            {'property': '/files', 'description': "should have required property 'files'"},
            {'property': '/project/title', 'description': "should have required property 'title'"},
            {'property': '/project/description', 'description': 'must NOT have more than 5000 characters'},
            {'property': '/project/taxId', 'description': "must have required property 'taxId'"},
            {'property': '/project/holdDate', 'description': 'must match format "date"'},
            {'property': '/analysis/0/description',
             'description': "should have required property 'description'"},
            {'property': '/analysis/0/referenceGenome',
             'description': "should have required property 'referenceGenome'"},
            {'property': '/sample/0/bioSampleAccession',
             'description': "should have required property 'bioSampleAccession'"},
            {'property': '/sample/0/bioSampleObject',
             'description': "should have required property 'bioSampleObject'"},
            {'property': '/sample/0', 'description': 'should match exactly one schema in oneOf'},
            {'property': '/sample/3/bioSampleObject/name', 'description': "must have required property 'name'"},
            {'property': '/sample/3/bioSampleObject/characteristics/organism',
             'description': "must have required property 'organism'"},
            {'property': '/sample/3/bioSampleObject/characteristics/Organism',
             'description': "must have required property 'Organism'"},
            {'property': '/sample/3/bioSampleObject/characteristics/species',
             'description': "must have required property 'species'"},
            {'property': '/sample/3/bioSampleObject/characteristics/Species',
             'description': "must have required property 'Species'"},
            {'property': '/sample/3/bioSampleObject/characteristics',
             'description': 'must match a schema in anyOf'},
            {'property': '/project/childProjects/1', 'description': 'PRJEBNA does not exist or is private'},
            {'property': '/sample/2/bioSampleObject/characteristics/taxId',
             'description': '1234 is not a valid taxonomy code'},
            {'property': '/sample/1/bioSampleObject/characteristics/Organism',
             'description': 'Species sheep sapiens does not match taxonomy 9606 (Homo sapiens)'},
            {'property': '/sample/analysisAlias', 'description': 'alias1 present in Analysis not in Samples'},
            {'property': '/sample/analysisAlias',
             'description': 'alias_1,alias_2 present in Samples not in Analysis'},
        ],
        'spreadsheet_errors': [
            {'sheet': '', 'row': '', 'column': '',
             'description': 'Error loading problem.xlsx: Exception()'}
        ]
    }
}


class TestValidator(TestCase):
    resource_dir = os.path.join(os.path.dirname(__file__), 'resources')
    vcf_files = os.path.join(resource_dir, 'vcf_files')
    fasta_files = os.path.join(resource_dir, 'fasta_files')
    assembly_reports = os.path.join(resource_dir, 'assembly_reports')
    output_dir = os.path.join(resource_dir, 'validation_reports')
    mapping_file = os.path.join(output_dir, 'vcf_files_mapping.csv')
    metadata_xlsx_file = os.path.join(resource_dir, 'EVA_Submission_test.xlsx')
    metadata_json_file = os.path.join(resource_dir, 'metadata_with_filename.json')

    def setUp(self) -> None:
        # create vcf mapping file
        os.makedirs(self.output_dir, exist_ok=True)
        create_mapping_file(self.mapping_file,
                            [os.path.join(self.vcf_files, 'input_passed.vcf')],
                            [os.path.join(self.fasta_files, 'input_passed.fa')],
                            [os.path.join(self.assembly_reports, 'input_passed.txt')])
        self.validator = Validator(self.mapping_file, self.output_dir, metadata_xlsx=self.metadata_xlsx_file)
        self.validator_json = Validator(self.mapping_file, self.output_dir, metadata_json=self.metadata_json_file)
        # Backup metadata json file so can restore after tests
        self.backup_metadata_json = f'{self.metadata_json_file}.backup'
        shutil.copy(self.metadata_json_file, self.backup_metadata_json)

    def tearDown(self) -> None:
        files_from_tests = [
            self.mapping_file,
            os.path.join(self.output_dir, VALIDATION_OUTPUT_DIR, 'other_validations',
                         'metadata_spreadsheet_validation.txt'),
            os.path.join(self.output_dir, VALIDATION_OUTPUT_DIR, 'report.html'),
            os.path.join(self.output_dir, VALIDATION_OUTPUT_DIR, 'report.txt')
        ]
        for f in files_from_tests:
            if os.path.exists(f):
                os.remove(f)
        # Restore metadata json file
        shutil.move(self.backup_metadata_json, self.metadata_json_file)

    def format_data_structure(self, source):
        if isinstance(source, dict):
            return {k: self.format_data_structure(v) for k, v in source.items()}
        elif isinstance(source, list):
            return [self.format_data_structure(v) for v in source]
        elif isinstance(source, str):
            return source.format(resource_dir=self.resource_dir)
        else:
            return source

    def run_collect_results(self, validator_to_run):
        validator_to_run._collect_validation_workflow_results()
        # Drop report paths from comparison (test will fail if missing)
        del validator_to_run.results['metadata_check']['json_report_path']
        if 'spreadsheet_report_path' in validator_to_run.results['metadata_check']:
            del validator_to_run.results['metadata_check']['spreadsheet_report_path']
        del validator_to_run.results['sample_check']['report_path']
        for file in validator_to_run.results['vcf_check'].values():
            del file['report_path']
        for file in validator_to_run.results['assembly_check'].values():
            del file['report_path']

    def test__collect_validation_workflow_results_with_metadata_json(self):
        self.run_collect_results(self.validator_json)
        assert self.validator_json.results == self.format_data_structure(expected_validation_results)

    def test__collect_validation_workflow_results_with_metadata_xlsx(self):
        expected_results = deepcopy(expected_validation_results)
        expected_results['metadata_check']['spreadsheet_errors'] = [
            # NB. Wouldn't normally get conversion error + validation errors together, but it is supported.
            {'sheet': '', 'row': '', 'column': '',
             'description': 'Error loading problem.xlsx: Exception()'},
            {'sheet': 'Files', 'row': '', 'column': '', 'description': 'Sheet "Files" is missing'},
            {'sheet': 'Project', 'row': 3, 'column': 'Project Title',
             'description': 'Column "Project Title" is not populated'},
            {'sheet': 'Project', 'row': 3, 'column': 'Description',
             'description': 'must NOT have more than 5000 characters'},
            {'sheet': 'Project', 'row': 3, 'column': 'Taxonomy ID',
             'description': 'Column "Taxonomy ID" is not populated'},
            {'sheet': 'Project', 'row': 3, 'column': 'Hold Date',
             'description': 'must match format "date"'},
            {'sheet': 'Analysis', 'row': 2, 'column': 'Description',
             'description': 'Column "Description" is not populated'},
            {'sheet': 'Analysis', 'row': 2, 'column': 'Reference',
             'description': 'Column "Reference" is not populated'},
            {'sheet': 'Sample', 'row': 3, 'column': 'Sample Accession',
             'description': 'Column "Sample Accession" is not populated'},
            {'sheet': 'Sample', 'row': 6, 'column': 'BioSample Name',
             'description': 'Column "BioSample Name" is not populated'},
            {'sheet': 'Sample', 'row': 6, 'column': 'Scientific Name',
             'description': 'Column "Scientific Name" is not populated'},
            {'sheet': 'Project', 'row': 3, 'column': 'Child Project(s)',
             'description': 'PRJEBNA does not exist or is private'},
            {'sheet': 'Sample', 'row': 5, 'column': 'Taxonomy ID',
             'description': '1234 is not a valid taxonomy code'},
            {'sheet': 'Sample', 'row': '', 'column': 'Analysis Alias',
             'description': 'alias1 present in Analysis not in Samples'},
            {'sheet': 'Sample', 'row': '', 'column': 'Analysis Alias',
             'description': 'alias_1,alias_2 present in Samples not in Analysis'}
        ]

        self.run_collect_results(self.validator)
        assert self.validator.results == self.format_data_structure(expected_results)

    def test_create_report(self):
        self.validator._collect_validation_workflow_results()
        html_report, text_report = self.validator.create_reports()
        assert os.path.exists(html_report)
        assert os.path.exists(text_report)

    def test_parse_biovalidator_validation_results(self):
        self.validator.results['metadata_check'] = {}
        self.validator.collect_biovalidator_validation_results()
        assert self.validator.results['metadata_check']['json_errors'] == [
            {'property': '/files', 'description': "should have required property 'files'"},
            {'property': '/project/title', 'description': "should have required property 'title'"},
            {'property': '/project/description', 'description': 'must NOT have more than 5000 characters'},
            {'property': '/project/taxId', 'description': "must have required property 'taxId'"},
            {'property': '/project/holdDate', 'description': 'must match format "date"'},
            {'property': '/analysis/0/description', 'description': "should have required property 'description'"},
            {'property': '/analysis/0/referenceGenome',
             'description': "should have required property 'referenceGenome'"},
            {'property': '/sample/0/bioSampleAccession',
             'description': "should have required property 'bioSampleAccession'"},
            {'property': '/sample/0/bioSampleObject', 'description': "should have required property 'bioSampleObject'"},
            {'property': '/sample/0', 'description': 'should match exactly one schema in oneOf'},
            {'property': '/sample/3/bioSampleObject/name', 'description': "must have required property 'name'"},
            {'property': '/sample/3/bioSampleObject/characteristics/organism',
             'description': "must have required property 'organism'"},
            {'property': '/sample/3/bioSampleObject/characteristics/Organism',
             'description': "must have required property 'Organism'"},
            {'property': '/sample/3/bioSampleObject/characteristics/species',
             'description': "must have required property 'species'"},
            {'property': '/sample/3/bioSampleObject/characteristics/Species',
             'description': "must have required property 'Species'"},
            {'property': '/sample/3/bioSampleObject/characteristics', 'description': 'must match a schema in anyOf'}
        ]

    def test_convert_biovalidator_validation_to_spreadsheet(self):
        self.validator.results['metadata_check'] = {
            'json_errors': [
                {'property': '/files', 'description': "should have required property 'files'"},
                {'property': '/project/title', 'description': "should have required property 'title'"},
                {'property': '/project/taxId', 'description': "must have required property 'taxId'"},
                {'property': '/project/holdDate', 'description': 'must match format "date"'},
                {'property': '/analysis/0/description',
                 'description': "should have required property 'description'"},
                {'property': '/analysis/0/referenceGenome',
                 'description': "should have required property 'referenceGenome'"},
                {'property': '/sample/0/bioSampleAccession',
                 'description': "should have required property 'bioSampleAccession'"},
                {'property': '/sample/0/bioSampleObject',
                 'description': "should have required property 'bioSampleObject'"},
                {'property': '/sample/0', 'description': 'should match exactly one schema in oneOf'},
                # Missing BioSamples attributes
                {'property': '/sample/3/bioSampleObject/name',
                 'description': "must have required property 'name'"},
                {'property': '/sample/3/bioSampleObject/characteristics/organism',
                 'description': "must have required property 'organism'"},
                {'property': '/sample/3/bioSampleObject/characteristics/Organism',
                 'description': "must have required property 'Organism'"},
                {'property': '/sample/3/bioSampleObject/characteristics/species',
                 'description': "must have required property 'species'"},
                {'property': '/sample/3/bioSampleObject/characteristics/Species',
                 'description': "must have required property 'Species'"},
                {'property': '/sample/3/bioSampleObject/characteristics',
                 'description': 'must match a schema in anyOf'},
                # Semantic checks
                {'property': '/project/childProjects/1', 'description': 'PRJEBNA does not exist or is private'},
                {'property': '/sample/2/bioSampleObject/characteristics/taxId',
                 'description': '1234 is not a valid taxonomy code'},
                {'property': '/sample/analysisAlias', 'description': 'alias1 present in Analysis not in Samples'},
                {'property': '/sample/analysisAlias',
                 'description': 'alias_1,alias_2 present in Samples not in Analysis'},
                {'property': '/sample/0/bioSampleAccession',
                 'description': "Existing sample SAMEA6675477 must have required property 'collection date'"}
            ]
        }
        self.validator._convert_biovalidator_validation_to_spreadsheet()

        assert self.validator.results['metadata_check']['spreadsheet_errors'] == [
            {'sheet': 'Files', 'row': '', 'column': '', 'description': 'Sheet "Files" is missing'},
            {'sheet': 'Project', 'row': 3, 'column': 'Project Title',
             'description': 'Column "Project Title" is not populated'},
            {'sheet': 'Project', 'row': 3, 'column': 'Taxonomy ID',
             'description': 'Column "Taxonomy ID" is not populated'},
            {'sheet': 'Project', 'row': 3, 'column': 'Hold Date',
             'description': 'must match format "date"'},
            {'sheet': 'Analysis', 'row': 2, 'column': 'Description',
             'description': 'Column "Description" is not populated'},
            {'sheet': 'Analysis', 'row': 2, 'column': 'Reference',
             'description': 'Column "Reference" is not populated'},
            {'sheet': 'Sample', 'row': 3, 'column': 'Sample Accession',
             'description': 'Column "Sample Accession" is not populated'},
            {'sheet': 'Sample', 'row': 6, 'column': 'BioSample Name',
             'description': 'Column "BioSample Name" is not populated'},
            {'sheet': 'Sample', 'row': 6, 'column': 'Scientific Name',
             'description': 'Column "Scientific Name" is not populated'},
            {'sheet': 'Project', 'row': 3, 'column': 'Child Project(s)',
             'description': 'PRJEBNA does not exist or is private'},
            {'sheet': 'Sample', 'row': 5, 'column': 'Taxonomy ID', 'description': '1234 is not a valid taxonomy code'},
            {'sheet': 'Sample', 'row': '', 'column': 'Analysis Alias',
             'description': 'alias1 present in Analysis not in Samples'},
            {'sheet': 'Sample', 'row': '', 'column': 'Analysis Alias',
             'description': 'alias_1,alias_2 present in Samples not in Analysis'},
            {'column': 'Sample Accession', 'row': 3, 'sheet': 'Sample',
             'description': 'Existing sample SAMEA6675477 must have required property '
                            "'collection date'"}
        ]

    def test_collect_conversion_errors(self):
        self.validator.results['metadata_check'] = {}
        self.validator._load_spreadsheet_conversion_errors()
        assert self.validator.results['metadata_check']['spreadsheet_errors'] == [{
            'column': '',
            'description': 'Error loading problem.xlsx: Exception()',
            'row': '',
            'sheet': ''
        }]

    def test_get_vcf_fasta_analysis_mapping(self):
        prev_metadata_json_value = self.validator_json.metadata_json
        metadata_path = os.path.join(self.resource_dir, 'metadata_with_filename.json')
        self.validator_json.metadata_json = metadata_path
        # Change directory so filenames in metadata are resolvable
        os.chdir(self.vcf_files)
        result = self.validator_json.get_vcf_fasta_analysis_mapping()
        assert len(result) == 1
        assert result[0]['vcf_file'].endswith('input_passed.vcf')
        assert result[0]['fasta_file'].endswith('input_passed.fa')
        assert result[0]['analysis'] == 'AA'

        # Also works from any directory if metadata contains full paths
        os.chdir(os.path.dirname(__file__))
        metadata = EvaMetadataJson(metadata_path)
        updated_files = metadata.files
        for file_obj in updated_files:
            file_obj['fileName'] = os.path.join(self.vcf_files, file_obj['fileName'])
        metadata.set_files(updated_files)
        updated_metadata = os.path.join(self.resource_dir, 'updated_metadata.json')
        metadata.write(updated_metadata)

        self.validator_json.metadata_json = updated_metadata
        result = self.validator_json.get_vcf_fasta_analysis_mapping()
        assert len(result) == 1
        assert result[0]['vcf_file'].endswith('input_passed.vcf')
        assert result[0]['fasta_file'].endswith('input_passed.fa')
        assert result[0]['analysis'] == 'AA'

        if os.path.exists(updated_metadata):
            os.remove(updated_metadata)
        # Reset metadata_json in case other tests need it
        self.validator_json.metadata_json = prev_metadata_json_value

    def test__update_metadata_with_evidence_type_success(self):
        self.validator_json.results['evidence_type_check'] = {
            'AA': {
                'errors': None,
                'evidence_type': 'allele_frequency'
            },
            'report_path': '{resource_dir}/validation_reports/validation_output/other_validations/evidence_type_checker.yml'
        }
        self.validator_json._update_metadata_with_evidence_type()

        # Analysis updated with evidence type
        updated_metadata = EvaMetadataJson(self.validator_json.metadata_json_post_validation)
        assert updated_metadata.analyses[0]['evidenceType'] == 'allele_frequency'

    def test__update_metadata_with_evidence_type_failure(self):
        self.validator_json.results['evidence_type_check'] = {
            'AA': {
                'errors': ['VCF file evidence type could not be determined'],
                'evidence_type': None
            },
            'report_path': '{resource_dir}/validation_reports/validation_output/other_validations/evidence_type_checker.yml'
        }
        self.validator_json._update_metadata_with_evidence_type()

        # Nothing added to analysis
        updated_metadata = EvaMetadataJson(self.validator_json.metadata_json_post_validation)
        assert 'evidenceType' not in updated_metadata.analyses[0]

    def test__update_metadata_with_evidence_type_did_not_run(self):
        self.validator_json.results['evidence_type_check'] = {}
        self.validator_json._update_metadata_with_evidence_type()

        # Nothing added to analysis
        updated_metadata = EvaMetadataJson(self.validator_json.metadata_json_post_validation)
        assert 'evidenceType' not in updated_metadata.analyses[0]

    def test__check_consent_statement_is_needed_for_submission(self):
        self.validator_json.results['evidence_type_check'] = {
            'AA': {
                'errors': None,
                'evidence_type': 'genotype'
            },
            'report_path': '{resource_dir}/validation_reports/validation_output/other_validations/evidence_type_checker.yml'
        }
        assert self.validator_json._check_consent_statement_is_needed_for_submission() is True





