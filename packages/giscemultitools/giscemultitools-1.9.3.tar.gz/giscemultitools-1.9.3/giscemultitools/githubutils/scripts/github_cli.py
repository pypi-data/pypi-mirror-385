import click
from json import dumps


@click.group()
def github_cli():
    pass


@click.command('get-commits-sha-from-merge-commit')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--sha", help="Merge commit sha", required=True, type=click.STRING)
def get_commits_sha_from_merge_commit(owner, repository, sha):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.get_commits_sha_from_merge_commit(owner=owner, repository=repository, sha=sha)
    print(dumps(res))


@click.command('get-pr-from-sha-merge-commit')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--sha", help="Merge commit sha", required=True, type=click.STRING)
def get_pr_from_sha_merge_commit(owner, repository, sha):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.get_pr_from_sha_merge_commit(owner=owner, repository=repository, sha=sha)
    print(dumps(res))


@click.command('get-pullrequest-info')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--pr", help="PR number", required=True, type=click.STRING)
def get_pullrequest_info(owner, repository, pr):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.get_pullrequest_info(owner=owner, repository=repository, pr_number=pr)
    print(dumps(res))


@click.command('get-pullrequest-checks')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--pr", help="PR number", required=True, type=click.STRING)
@click.option("--include-skyped", help="To get skyped checks too", default=False, type=click.BOOL, is_flag=True)
def get_pullrequest_checks(owner, repository, pr, include_skyped):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.get_pullrequest_checks(owner=owner, repository=repository, pr_number=pr, include_skyped=include_skyped)
    print(dumps(res))


@click.command('get-pullrequest-check-status')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--pr", help="PR number", required=True, type=click.STRING)
@click.option("--check-name", help="Check name", required=True, type=click.STRING)
@click.option("--include-skyped", help="To get skyped checks too", default=False, type=click.BOOL, is_flag=True)
def get_pullrequest_check_status(owner, repository, pr, check_name, include_skyped):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.get_pullrequest_check_status(
        owner=owner, repository=repository, pr_number=pr, check_name=check_name, include_skyped=include_skyped
    )
    print(dumps(res))


@click.command('get-pullrequest-context-checks')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--pr", help="PR number", required=True, type=click.STRING)
def get_pullrequest_context_checks(owner, repository, pr):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.get_pullrequest_context_checks(owner=owner, repository=repository, pr_number=pr)
    print(dumps(res))


@click.command('get-pullrequest-context-check-status')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--pr", help="PR number", required=True, type=click.STRING)
@click.option("--check-name", help="Check name", required=True, type=click.STRING)
def get_pullrequest_context_check_status(owner, repository, pr, check_name):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.get_pullrequest_context_check_status(
        owner=owner, repository=repository, pr_number=pr, check_name=check_name
    )
    print(dumps(res))


@click.command('update-projectv2-card-from-id')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--project-id", help="Project ID", required=True, type=click.STRING)
@click.option("--item-id", help="Item ID", required=True, type=click.STRING)
@click.option("--field-id", help="Field ID", required=True, type=click.STRING)
@click.option("--value", help="Text value", required=True, type=click.STRING)
def update_projectv2_card_from_id(owner, repository, project_id, item_id, field_id, value):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.update_projectv2_item_field_value(owner, repository, project_id, item_id, field_id, value)
    print(dumps(res))


@click.command('add-item-to-projectv2')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--project-id", help="Project ID", required=True, type=click.STRING)
@click.option("--item-id", help="Item ID", required=True, type=click.STRING)
def add_item_to_projectv2(owner, repository, project_id, item_id):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.add_item_to_project(owner, repository, project_id, item_id)
    print(dumps(res))


@click.command('add-prs-to-projectv2')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--project-name", help="Project name", required=True, type=click.STRING)
@click.option("--prs", help="List of prs separated", required=True, type=click.STRING)
def add_prs_to_projectv2(owner, repository, project_name, prs):
    prs = [_pr.replace(' ', '') for _pr in prs.split(',')]
    from giscemultitools.githubutils.utils import GithubUtils
    GithubUtils.add_prs_to_project_by_name(owner, repository, project_name, prs)


@click.command('project-changelog')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--project-name", help="Project ID", required=True, type=click.STRING)
@click.option('--date-since', help='Change log date from ex. 2022-12-27', default=None, show_default=True, type=click.STRING)
def project_changelog(owner, repository, project_name, date_since):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.project_changelog(owner, repository, project_name, date_since=date_since)
    changelog = GithubUtils.format_changelog(res, 'markdown')
    print(changelog)


@click.command('project-changelog-v2')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--project-name", help="Project ID", required=True, type=click.STRING)
@click.option('--date-since', help='Change log date from ex. 2022-12-27', default=None, show_default=True, type=click.STRING)
@click.option('--format', 'output_format', help='Output format', default='markdown', show_default=True, type=click.Choice(['markdown']))
def project_changelog_v2_cli(owner, repository, project_name, date_since, output_format):
    from giscemultitools.githubutils.utils import GithubUtils
    changelog_data = GithubUtils.project_changelog_v2(owner, repository, project_name, date_since=date_since)
    changelog = GithubUtils.format_changelog_v2(changelog_data, project_name, output_format=output_format)
    print(changelog)


@click.command('get-pullrequests-from-project-by-status')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--project-name", help="Project ID", required=True, type=click.STRING)
@click.option("--card-status", help="Project ID", required=True, type=click.STRING)
def get_pullrequests_from_project_by_status(owner, repository, project_name, card_status):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.get_pulls_from_project_and_column(owner, repository, project_name, card_status)
    print(dumps(res))


@click.command('get-pullrequests-commits-from-project-by-status')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--project-name", help="Project ID", required=True, type=click.STRING)
@click.option("--card-status", help="Project ID", required=True, type=click.STRING)
def get_pullrequests_commits_from_project_by_status(owner, repository, project_name, card_status):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.get_pulls_from_project_and_column(owner, repository, project_name, card_status)
    res = [GithubUtils.get_pullrequest_info(owner, repository, _pr["number"]) for _pr in res]
    print(dumps(res))


@click.command('projects-by-name')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--project-pattern", help="Project name pattern", required=True, type=click.STRING)
@click.option("--only-one", help="To get only one result", default=False, type=click.BOOL, is_flag=True)
def project_by_name(owner, repository, project_pattern, only_one):
    from giscemultitools.githubutils.objects import GHAPIRequester
    res = GHAPIRequester(owner, repository).get_project_info_from_project_name(project_pattern, only_one=only_one)
    print(dumps(res))


@click.command('find-pullrequests-by-description')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option('--term', help='Term to locate inside PR descriptions', required=True, type=click.STRING)
@click.option('--state', help='Pull request state filter', default='all', show_default=True, type=click.Choice(['open', 'closed', 'merged', 'all']))
def find_pullrequests_by_description(owner, repository, term, state):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.find_pullrequests_by_description(owner=owner, repository=repository, term=term, state=state)
    print(dumps(res))


@click.command('find-pullrequests-by-branch')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option('--fragment', help='Substring to match inside the head branch name', required=True, type=click.STRING)
@click.option('--state', help='Pull request state filter', default='all', show_default=True, type=click.Choice(['open', 'closed', 'merged', 'all']))
def find_pullrequests_by_branch(owner, repository, fragment, state):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.find_pullrequests_by_branch_fragment(owner=owner, repository=repository, fragment=fragment, state=state)
    print(dumps(res))


@click.command('get-latest-milestone')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option('--state', help='Milestone state filter', default='open', show_default=True, type=click.Choice(['open', 'closed', 'all']))
def get_latest_milestone(owner, repository, state):
    from giscemultitools.githubutils.utils import GithubUtils
    milestone = GithubUtils.get_latest_milestone(owner=owner, repository=repository, state=state)
    print(dumps(milestone))


@click.command('set-pullrequest-milestone')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--pr", help="PR number", required=True, type=click.INT)
@click.option("--milestone", help="Milestone number", required=True, type=click.INT)
def set_pullrequest_milestone(owner, repository, pr, milestone):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.set_pullrequest_milestone(owner=owner, repository=repository, pr_number=pr, milestone=milestone)
    print(dumps(res))


@click.command('set-open-pullrequests-milestone')
@click.option('--owner', help='GitHub owner name', default='gisce', show_default=True)
@click.option('--repository', help='GitHub repository name', default='erp', show_default=True)
@click.option("--milestone", help="Target milestone number (defaults to latest)", default=None, type=click.INT)
@click.option('--state', help='Pull request state filter', default='open', show_default=True, type=click.Choice(['open', 'closed', 'all']))
def set_open_pullrequests_milestone(owner, repository, milestone, state):
    from giscemultitools.githubutils.utils import GithubUtils
    res = GithubUtils.set_open_pullrequests_milestone(owner=owner, repository=repository, milestone=milestone, state=state)
    print(dumps(res))


github_cli.add_command(get_commits_sha_from_merge_commit)
github_cli.add_command(update_projectv2_card_from_id)
github_cli.add_command(get_pullrequest_info)
github_cli.add_command(project_changelog)
github_cli.add_command(project_changelog_v2_cli)
github_cli.add_command(project_by_name)
github_cli.add_command(get_pullrequest_checks)
github_cli.add_command(get_pr_from_sha_merge_commit)
github_cli.add_command(get_pullrequest_check_status)
github_cli.add_command(get_pullrequest_context_checks)
github_cli.add_command(get_pullrequest_context_check_status)
github_cli.add_command(get_pullrequests_from_project_by_status)
github_cli.add_command(get_pullrequests_commits_from_project_by_status)
github_cli.add_command(add_item_to_projectv2)
github_cli.add_command(add_prs_to_projectv2)
github_cli.add_command(find_pullrequests_by_description)
github_cli.add_command(find_pullrequests_by_branch)
github_cli.add_command(get_latest_milestone)
github_cli.add_command(set_pullrequest_milestone)
github_cli.add_command(set_open_pullrequests_milestone)


if __name__ == "__main__":
    github_cli()
