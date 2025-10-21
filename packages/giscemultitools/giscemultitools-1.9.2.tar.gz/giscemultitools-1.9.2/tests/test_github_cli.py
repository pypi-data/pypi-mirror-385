# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest

try:  # pragma: no cover - compatibility shim
    from unittest import mock
except ImportError:  # pragma: no cover
    import mock  # type: ignore

from click.testing import CliRunner

from giscemultitools.githubutils.scripts.github_cli import github_cli


class GithubCliMilestoneTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch('giscemultitools.githubutils.utils.GithubUtils.get_latest_milestone')
    def test_get_latest_milestone_cli_fetches_and_outputs(self, mock_latest):
        mock_latest.return_value = {'number': 9}

        result = self.runner.invoke(
            github_cli,
            [
                'get-latest-milestone',
                '--owner', 'team',
                '--repository', 'repo',
                '--state', 'closed'
            ]
        )

        self.assertEqual(result.exit_code, 0)
        mock_latest.assert_called_once_with(owner='team', repository='repo', state='closed')
        self.assertIn('"number": 9', result.output)

    @mock.patch('giscemultitools.githubutils.utils.GithubUtils.set_pullrequest_milestone')
    def test_set_pullrequest_milestone_cli_passes_arguments(self, mock_set_milestone):
        mock_set_milestone.return_value = {'ok': True}

        result = self.runner.invoke(
            github_cli,
            [
                'set-pullrequest-milestone',
                '--pr', '42',
                '--milestone', '7'
            ]
        )

        self.assertEqual(result.exit_code, 0)
        mock_set_milestone.assert_called_once_with(owner='gisce', repository='erp', pr_number=42, milestone=7)
        self.assertIn('"ok": true', result.output)

    @mock.patch('giscemultitools.githubutils.utils.GithubUtils.set_open_pullrequests_milestone')
    def test_set_open_pullrequests_milestone_cli_handles_optional_milestone(self, mock_bulk_set):
        mock_bulk_set.return_value = [{'pull_request': 1}]

        result = self.runner.invoke(
            github_cli,
            [
                'set-open-pullrequests-milestone',
                '--milestone', '15',
                '--state', 'all'
            ]
        )

        self.assertEqual(result.exit_code, 0)
        mock_bulk_set.assert_called_once_with(owner='gisce', repository='erp', milestone=15, state='all')
        self.assertIn('"pull_request": 1', result.output)

    @mock.patch('giscemultitools.githubutils.utils.GithubUtils.find_pullrequests_by_description')
    def test_find_pullrequests_by_description_cli_passes_arguments(self, mock_find):
        mock_find.return_value = [{'number': 1}]

        result = self.runner.invoke(
            github_cli,
            [
                'find-pullrequests-by-description',
                '--term', 'TASK-79573',
                '--state', 'open'
            ]
        )

        self.assertEqual(result.exit_code, 0)
        mock_find.assert_called_once_with(owner='gisce', repository='erp', term='TASK-79573', state='open')
        self.assertIn('"number": 1', result.output)

    @mock.patch('giscemultitools.githubutils.utils.GithubUtils.find_pullrequests_by_branch_fragment')
    def test_find_pullrequests_by_branch_cli_passes_arguments(self, mock_find):
        mock_find.return_value = [{'head_ref': 'feature/TASK-79573'}]

        result = self.runner.invoke(
            github_cli,
            [
                'find-pullrequests-by-branch',
                '--fragment', '79573',
                '--state', 'merged'
            ]
        )

        self.assertEqual(result.exit_code, 0)
        mock_find.assert_called_once_with(owner='gisce', repository='erp', fragment='79573', state='merged')
        self.assertIn('feature/TASK-79573', result.output)
