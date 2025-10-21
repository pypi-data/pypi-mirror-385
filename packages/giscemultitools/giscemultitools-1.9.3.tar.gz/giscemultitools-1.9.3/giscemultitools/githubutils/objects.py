# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import requests
import os
from json import loads, dumps


class RepositorySetUp(object):
    def __init__(self, owner, repository):
        self.owner = owner
        self.repository = repository


class GHAPIRequester(RepositorySetUp):
    def __init__(self, owner, repository):
        super(GHAPIRequester, self).__init__(owner, repository)
        if not os.environ.get('GITHUB_TOKEN'):
            raise EnvironmentError('Missing GITHUB_TOKEN environment variable')
        self.headers = {'Authorization': 'token {}'.format(os.environ.get('GITHUB_TOKEN'))}
        self.base_url = 'https://api.github.com/repos/{}/{}/'.format(self.owner, self.repository)
        self.graphql_url = 'https://api.github.com/graphql'
        self.search_url = 'https://api.github.com/search/issues'
        self._last_pull_request_truncated = False

    def _request(self, url, params=None):
        r = requests.get(url, headers=self.headers, params=params)
        return loads(r.text)

    def _patch(self, url, payload):
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
        if response.text:
            return loads(response.text)
        return {}

    def _graphql_request(self, data):
        r = requests.post(self.graphql_url, data=data, headers=self.headers)
        return loads(r.text)

    def get_pulls_from_sha(self, sha):
        return self._request("{}commits/{}/pulls".format(self.base_url, sha))

    def get_commits_from_pr(self, pr):
        return self._request("{}pulls/{}/commits?per_page=100".format(self.base_url, pr))

    def get_project_info_from_project_name(self, project_name, only_one=False):
        query = """
            query {
                repository(owner: "%s", name: "%s") {
                    projectsV2(query: "name: %s", first: 60){
                        nodes {
                            id
                            number
                            title
                        }
                    }
                }
            }
        """ % (self.owner, self.repository, project_name)
        try:
            res = self._graphql_request(dumps({'query': query}))
            if only_one:
                return res['data']['repository']['projectsV2']['nodes'][0]
            else:
                return res['data']['repository']['projectsV2']['nodes']
        except Exception:
            raise UserWarning("{project_name} Not found".format(project_name=project_name))

    def get_pulls_from_project(self, project_name, pr_states=('merged',), project_status=('Done',)):
        pr_states = ','.join(pr_states)
        project_info = self.get_project_info_from_project_name(project_name, only_one=True)
        prs = []

        query = """
        {
          search(first: 100, query: "repo:%s/%s is:pr is:%s project:%s/%s", type: ISSUE) {
            edges {
              node {
                ... on PullRequest {
                  title
                  url
                  mergedAt
                  number
                  labels(first: 20){
                    nodes {
                      name
                    }
                  }
                  projectItems(first: 10) {
                    nodes {
                        project { id title number url }
                        id
                        type
                        fieldValues(last: 10) {
                            nodes {
                                ... on ProjectV2ItemFieldSingleSelectValue {
                                    id
                                    name
                                    updatedAt
                                    field {
                                      ... on ProjectV2SingleSelectField {
                                        id
                                        name
                                        options {
                                            name
                                            id
                                          }
                                      }
                                    }
                                }
                            }
                        }
                    }
                  }
                }
              }
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
        """ % (self.owner, self.repository, pr_states, self.owner, project_info['number'])
        first_result = self._graphql_request(dumps({'query': query}))
        cursor = first_result['data']['search']['pageInfo']['endCursor']
        has_next = first_result['data']['search']['pageInfo']['hasNextPage']
        for pr in first_result['data']['search']['edges']:
            status = [
                (_field['name'], _field['updatedAt']) for _field in
                [
                    _project_item
                    for _project_item in pr['node'].pop('projectItems')['nodes']
                    if _project_item['project']['title'] == project_name
                ][0]['fieldValues']['nodes']
                if _field.get('field', {}).get('name') == 'Status'
            ][0]
            if status[0] in project_status:
                pr['node']['labels'] = [_label['name'] for _label in pr['node']['labels']['nodes']]
                pr['node']['status_change_date'] = status[1]
                prs.append(pr['node'])

        next_query = """
        {
          search(first: 100, after: "%s", query: "repo:%s/%s is:pr is:%s project:%s/%s", type: ISSUE) {
            edges {
              node {
                ... on PullRequest {
                  title
                  url
                  mergedAt
                  number
                  labels(first: 20){
                    nodes {
                      name
                    }
                  }
                  projectItems(first: 10) {
                    nodes {
                        project { id title number url }
                        id
                        type
                        fieldValues(last: 10) {
                            nodes {
                                ... on ProjectV2ItemFieldSingleSelectValue {
                                    id
                                    name
                                    updatedAt
                                    field {
                                      ... on ProjectV2SingleSelectField {
                                        id
                                        name
                                        options {
                                            name
                                            id
                                          }
                                      }
                                    }
                                }
                            }
                        }
                    }
                  }
                }
              }
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
        """

        while has_next:
            next_result = self._graphql_request(
                dumps(
                    {
                        'query': next_query % (cursor, self.owner, self.repository, pr_states, self.owner, project_info['number'])
                    }
                )
            )
            cursor = next_result['data']['search']['pageInfo']['endCursor']
            has_next = next_result['data']['search']['pageInfo']['hasNextPage']

            for pr in next_result['data']['search']['edges']:
                status = [
                    (_field['name'], _field['updatedAt']) for _field in
                    [
                        _project_item
                        for _project_item in pr['node'].pop('projectItems')['nodes']
                        if _project_item['project']['title'] == project_name
                    ][0]['fieldValues']['nodes']
                    if _field.get('field', {}).get('name') == 'Status'
                ][0]
                if status[0] in project_status:
                    pr['node']['labels'] = [_label['name'] for _label in pr['node']['labels']['nodes']]
                    pr['node']['status_change_date'] = status[1]
                    prs.append(pr['node'])

        return prs

    def get_pull_request_projects_and_commits(self, pull_request_number):
        # mergeCommit.oid is the hash
        query = """
            query {
                repository(owner: "%s", name: "%s") {
                    pullRequest(number: %s) {
                        id
                        baseRefName
                        number
                        state
                        url
                        title
                        mergedAt
                        createdAt

                        milestone {
                          title
                        }

                        mergeCommit {
                            oid
                        }

                        commits(first: 250){
                            nodes {
                              commit {
                                oid
                              }
                            }
                        }
                        labels(first: 20){
                            nodes {
                              name
                            }
                        }

                        projectItems(first: 10) {
                            nodes {
                                project { id title number url }
                                id
                                type
                                fieldValues(last: 10) {
                                    nodes {
                                        ... on ProjectV2ItemFieldSingleSelectValue {
                                            id
                                            name
                                            field {
                                              ... on ProjectV2SingleSelectField {
                                                id
                                                name
                                                options {
                                                    name
                                                    id
                                                  }
                                              }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """ % (self.owner, self.repository, pull_request_number)
        return self._graphql_request(dumps({'query': query}))

    def update_projectv2_item_field_value(self, project_id, item_id, field_column_id, value):
        query = """
            mutation MyMutation {
              updateProjectV2ItemFieldValue(
                input: {projectId: "%s", itemId: "%s", fieldId: "%s", value: {singleSelectOptionId: "%s"}}
              ) {
                  clientMutationId
                  projectV2Item {
                    id
                  }
                }
            }

        """ % (project_id, item_id, field_column_id, value)
        return self._graphql_request(dumps({'query': query}))

    def add_item_to_project_v2(self, project_id, item_id):
        query = """
            mutation {
              addProjectV2ItemById(input: {projectId: "%s", contentId: "%s"}) {
                item {
                  id
                }
              }
            }
        """ % (project_id, item_id)
        return self._graphql_request(dumps({'query': query}))

    def get_milestones(self, state='open', sort='due_on', direction='asc', per_page=100):
        milestones = []
        page = 1
        while True:
            params = {
                'state': state,
                'sort': sort,
                'direction': direction,
                'per_page': per_page,
                'page': page
            }
            response = self._request("{}milestones".format(self.base_url), params=params)
            if not isinstance(response, list) or not response:
                if isinstance(response, list):
                    milestones.extend(response)
                break
            milestones.extend(response)
            if len(response) < per_page:
                break
            page += 1
        return milestones

    def get_latest_milestone(self, state='open'):
        milestones = self.get_milestones(state=state)
        if not milestones:
            return None

        def _sort_key(item):
            due_on = item.get('due_on')
            created_at = item.get('created_at')
            return (due_on is None, due_on or created_at or '')

        milestones.sort(key=_sort_key)
        return milestones[-1]

    def get_pull_requests(self, state='open', per_page=100, max_pages=None):
        if state not in ('open', 'closed', 'all', 'merged'):
            raise ValueError('Unsupported pull request state {}'.format(state))

        self._last_pull_request_truncated = False
        pull_requests = []
        page = 1
        api_state = state
        merged_only = False
        if state == 'merged':
            api_state = 'closed'
            merged_only = True

        while True:
            if max_pages is not None and page > max_pages:
                self._last_pull_request_truncated = True
                break
            params = {
                'state': api_state,
                'per_page': per_page,
                'page': page
            }
            response = self._request("{}pulls".format(self.base_url), params=params)
            if not isinstance(response, list) or not response:
                if isinstance(response, list):
                    page_items = response
                else:
                    page_items = []
                if merged_only:
                    page_items = [pr for pr in page_items if pr.get('merged_at')]
                pull_requests.extend(page_items)
                break
            page_items = response
            filtered_items = [pr for pr in page_items if pr.get('merged_at')] if merged_only else page_items
            pull_requests.extend(filtered_items)
            if len(page_items) < per_page:
                break
            page += 1
        return pull_requests

    def update_pull_request_milestone(self, pull_request_number, milestone_number):
        payload = {'milestone': milestone_number}
        return self._patch("{}issues/{}".format(self.base_url, pull_request_number), payload)

    def search_pull_requests(self, term, search_in=None, state='all', per_page=100):
        if not term:
            raise ValueError('Search term cannot be empty')

        if state not in ('open', 'closed', 'merged', 'all'):
            raise ValueError('Unsupported pull request state {}'.format(state))

        query_parts = ['repo:{}/{}'.format(self.owner, self.repository), 'is:pr']

        if state in ('open', 'closed'):
            query_parts.append('is:{}'.format(state))
        elif state == 'merged':
            query_parts.append('is:merged')

        if search_in:
            if not isinstance(search_in, (tuple, list)):
                search_in = (search_in,)
            for field in search_in:
                query_parts.append('in:{}'.format(field))

        if '"' in term:
            term = term.replace('"', '\\"')
        query_parts.append('"{}"'.format(term))

        page = 1
        items = []
        while True:
            params = {
                'q': ' '.join(query_parts),
                'per_page': per_page,
                'page': page
            }
            response = self._request(self.search_url, params=params)
            page_items = response.get('items', [])
            items.extend(page_items)
            if len(page_items) < per_page:
                break
            page += 1
        return items

    def search_pull_requests_by_description(self, term, state='all'):
        return self.search_pull_requests(term, search_in=('body',), state=state)

    def find_pull_requests_by_branch_fragment(self, fragment, state='all'):
        if not fragment:
            raise ValueError('Branch fragment cannot be empty')

        fragment_lower = fragment.lower()
        state_qualifier = None
        if state == 'open':
            state_qualifier = 'state:open'
        elif state == 'closed':
            state_qualifier = 'state:closed'
        elif state == 'merged':
            state_qualifier = 'is:merged'
        elif state != 'all':
            raise ValueError('Unsupported pull request state {}'.format(state))

        base_parts = ['repo:{}/{}'.format(self.owner, self.repository), 'is:pr']
        if state_qualifier:
            base_parts.append(state_qualifier)

        def _build_query_parts(term):
            parts = list(base_parts)
            parts.append(term)
            return parts

        def _graphql_search(query_parts):
            candidates = []
            seen_numbers = set()
            graphql_query = """
                query($query: String!, $first: Int!, $after: String) {
                  search(query: $query, type: ISSUE, first: $first, after: $after) {
                    pageInfo {
                      hasNextPage
                      endCursor
                    }
                    nodes {
                      __typename
                      ... on PullRequest {
                        number
                        title
                        state
                        url
                        createdAt
                        updatedAt
                        mergedAt
                        headRefName
                        headRefOid
                        baseRefName
                        baseRefOid
                      }
                    }
                  }
                }
            """
            cursor = None
            while True:
                payload = {
                    'query': graphql_query,
                    'variables': {
                        'query': ' '.join(query_parts),
                        'first': 50,
                        'after': cursor
                    }
                }
                response = self._graphql_request(dumps(payload))
                if response.get('errors'):
                    return []
                search_data = response.get('data', {}).get('search', {})
                nodes = search_data.get('nodes', [])
                for node in nodes:
                    if not node or node.get('__typename') != 'PullRequest':
                        continue
                    head_ref = node.get('headRefName') or ''
                    if fragment_lower in head_ref.lower():
                        pr_number = node.get('number')
                        if pr_number not in seen_numbers:
                            candidates.append(
                                {
                                    'number': pr_number,
                                    'title': node.get('title'),
                                    'state': node.get('state'),
                                    'html_url': node.get('url'),
                                    'created_at': node.get('createdAt'),
                                    'updated_at': node.get('updatedAt'),
                                    'merged_at': node.get('mergedAt'),
                                    'head': {
                                        'ref': head_ref,
                                        'sha': node.get('headRefOid')
                                    },
                                    'base': {
                                        'ref': node.get('baseRefName'),
                                        'sha': node.get('baseRefOid')
                                    }
                                }
                            )
                            seen_numbers.add(pr_number)
                page_info = search_data.get('pageInfo') or {}
                if not page_info.get('hasNextPage'):
                    break
                cursor = page_info.get('endCursor')
            return candidates

        query_terms = []

        def _add_term(term):
            if term not in query_terms:
                query_terms.append(term)

        fragment_escaped = fragment.replace('"', '\\"')
        _add_term(fragment)
        _add_term('"{}"'.format(fragment_escaped))
        _add_term('head:"{}"'.format(fragment_escaped))
        if not fragment.startswith('*'):
            _add_term('head:{}*'.format(fragment_escaped))
            _add_term('head:*{}*'.format(fragment_escaped))

        aggregated_results = []
        seen_numbers = set()
        for term in query_terms:
            query_parts = _build_query_parts(term)
            for pull_request in _graphql_search(query_parts):
                pr_number = pull_request.get('number')
                if pr_number not in seen_numbers:
                    aggregated_results.append(pull_request)
                    seen_numbers.add(pr_number)
            if aggregated_results:
                break

        if aggregated_results:
            return aggregated_results

        rest_max_pages = 10
        pull_requests = self.get_pull_requests(state=state, max_pages=rest_max_pages)
        results = []
        for pull_request in pull_requests:
            head_ref = pull_request.get('head', {}).get('ref', '')
            if head_ref and fragment_lower in head_ref.lower():
                results.append(pull_request)
        if not results and self._last_pull_request_truncated:
            raise LookupError(
                'Branch fragment "{}" not found within the first {} pull request pages'.format(
                    fragment, rest_max_pages
                )
            )
        return results

    def get_pr_checks(self, pull_request_number):
        query = """
            query {
              repository(owner: "%s", name: "%s") {
                pullRequest(number: %s) {
                  commits(last: 1) {
                    nodes {
                      commit {

                        checkSuites(first: 100) {
                          nodes {
                            checkRuns(first: 100) {
                              nodes {
                                name
                                conclusion
                                permalink
                              }
                            }
                          }
                        }

                        status {
                          state
                          contexts {
                            state
                            targetUrl
                            description
                            context
                          }
                        }

                      }
                    }
                  }
                }
              }
            }
        """ % (
            self.owner, self.repository, pull_request_number
        )
        return self._graphql_request(dumps({'query': query}))
