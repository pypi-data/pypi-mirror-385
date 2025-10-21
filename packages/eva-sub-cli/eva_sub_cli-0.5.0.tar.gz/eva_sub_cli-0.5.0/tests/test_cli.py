import copy
import logging
import os
import shutil
import sys
from unittest import TestCase
from unittest.mock import patch, Mock


from eva_sub_cli import orchestrator
from eva_sub_cli.executables import cli
from tests.test_utils import touch


class TestCli(TestCase):

    resources_folder = os.path.join(os.path.dirname(__file__), 'resources')
    submission_dir = os.path.abspath(os.path.join(resources_folder, 'submission_dir'))

    def setUp(self) -> None:
        os.makedirs(self.submission_dir, exist_ok=True)

    def tearDown(self) -> None:
        if os.path.exists(self.submission_dir):
            shutil.rmtree(self.submission_dir)

    def test_main(self):
        args = Mock(submission_dir=self.submission_dir,
                    vcf_files=[], reference_fasta='', metadata_json=None, metadata_xlsx='',
                    tasks='validate', executor='native', debug=False)
        with patch('eva_sub_cli.executables.cli.parse_args', return_value=args), \
                patch('eva_sub_cli.orchestrator.orchestrate_process'):
            exit_status = cli.main()
            # Check that the debug message is shown
            logger = orchestrator.logger
            logger.debug('test')
            assert exit_status == 0
            # Log file should contain the log message
            log_file = os.path.join(self.submission_dir, 'eva_submission.log')
            with open(log_file) as open_log_file:
                all_lines = open_log_file.readlines()
                all_lines[0].endswith('[eva_sub_cli.orchestrator][DEBUG] test\n')

    def test_validate_args(self):
        vcf_file = os.path.join(self.submission_dir,'test.vcf')
        fasta_file = os.path.join(self.submission_dir, 'test.fasta')
        json_file = os.path.join(self.submission_dir, 'test.json')
        touch(vcf_file)
        touch(fasta_file)
        touch(json_file)
        cmd_args = [
            '--submission_dir', self.submission_dir,
            '--vcf_files', vcf_file,
            '--reference_fasta', fasta_file,
            '--metadata_json', json_file,
            '--tasks', 'validate',
            '--executor', 'native',
            '--debug'
        ]
        args = cli.parse_args(cmd_args)
        assert args.submission_dir == self.submission_dir


        with patch('sys.exit') as m_exit:
            cli.parse_args(cmd_args[:2]+cmd_args[4:])
            m_exit.assert_called_once_with(1)

