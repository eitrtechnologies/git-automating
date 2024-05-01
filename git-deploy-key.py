import requests
import logging
import argparse
from datetime import date
import json
import os

log = logging.getLogger(__name__)


class GitLabAPI:
    def __init__(self, gitlab_token, group_id, project_ids, recursive, export_results, remove_by_key):
        self.gitlab_token = gitlab_token
        self.group_id = group_id
        self.project_ids = project_ids
        self.export_results = export_results
        self.remove_by_key = remove_by_key
        self.recursive = recursive


    def _make_request(self, url, method='GET', headers=None, data=None):
        """
        Function to centralize http request to Gitlab's API

        """
        if not headers:
            headers = {"PRIVATE-TOKEN": self.gitlab_token}
        try:
            response = requests.request(method, url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.error("Error fetching from Gitlab API: %s", e)
            return {}, response.status_code
        try:
            return response.json(), response.status_code
        except ValueError:
            return response, response.status_code


    def _get_projects_info(self, url, headers=None):
        """
        Get projects' information
        """
        projects = []

        if not self.project_ids:
            # Get projects and subgroups within the group
            group_info_url = f"{url}/groups/{self.group_id}"
            group_info, _ = self._make_request(group_info_url, headers=headers)
            projects.extend(group_info.get('projects', []))

            if self.recursive:
                # Get subgroups within the group
                group_subgroups_url = f"{url}/groups/{self.group_id}/subgroups"
                subgroups, _ = self._make_request(group_subgroups_url, headers=headers)

                # Recursively get projects within subgroups
                for subgroup in subgroups:
                    subgroup_projects = self._get_subgroup_projects(url, subgroup['id'], headers)
                    projects.extend(subgroup_projects)
        else:
            for _id in self.project_ids:
                _url = f"{url}/projects/{_id}"
                response, _ = self._make_request(_url, headers=headers)
                projects.append(response)

        return projects


    def _get_subgroup_projects(self, url, group_id, headers=None):
        """
        Get projects within a subgroup
        """
        projects = []

        # Get projects within the subgroup
        subgroup_projects_url = f"{url}/groups/{group_id}/projects"
        subgroup_projects, _ = self._make_request(subgroup_projects_url, headers=headers)
        projects.extend(subgroup_projects)

        # Get subgroups within the subgroup
        subgroup_subgroups_url = f"{url}/groups/{group_id}/subgroups"
        subgroups, _ = self._make_request(subgroup_subgroups_url, headers=headers)

        # Recursively get projects within subgroups
        for subgroup in subgroups:
            subgroup_projects = self._get_subgroup_projects(url, subgroup['id'], headers)
            projects.extend(subgroup_projects)

        return projects


    def add_deploy_key(self, url, data, headers=None):
        """
        Add deploy key to a project

        """
        projects = self._get_projects_info(url, headers)

        for project in projects:
            _url = f"{url}/projects/{project['id']}/deploy_keys"
            response, status = self._make_request(_url, method='POST', headers=headers, data=data)
            self._export_results(response, status, "add", project['name'])


    def remove_deploy_key(self, url, deploy_key_title, deploy_key, projects=None, headers=None):
        """
        Remove deploy key from a project

        """
        projects = self._get_projects_info(url, headers)

        for project in projects:
            _url = f"{url}/projects/{project['id']}/deploy_keys"
            deploy_keys, _ = self._make_request(_url, headers=headers)

            if not self.remove_by_key:
                deploy_key = None

            for key in deploy_keys:
                if key['title'] == deploy_key_title or key['key'] == deploy_key:
                    _url = f"{url}/projects/{project['id']}/deploy_keys/{key['id']}"
                    response, status = self._make_request(_url, method='DELETE', headers=headers)
                    self._export_results(response, status, "remove", project['name'])
                

    def _export_results(self, response, status, action, project):
        """
        Export results
        
        """
        if self.export_results:
            print(f"{action}: {project}: status {status}: {response}")


def json_dict(value):
    try:
        return json.loads(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f'Invalid JSON: {e}')
    

def main():

    # Set commandline args
    parser = argparse.ArgumentParser(description='Utility script to enable or disable deploy key for projects in a GitLab group')

    parser.add_argument('--deploy-key-name', '-n', dest='deploy_key_title', type=str, help='Gitlab deploy key name, defaults to Key-YYYY-MM-DD')
    parser.add_argument('--deploy-key', '-d', dest='deploy_key', type=str, default=os.environ.get('GITLAB_DEPLOY_KEY', None), help='Gitlab deploy key id')
    parser.add_argument('--gitlab-token', '-t', dest='gitlab_token', type=str, default=os.environ.get('GITLAB_TOKEN', None), help='Gitlab token')
    parser.add_argument('--group-id', '-i', dest='group_id', type=int, help='Gitlab group id')
    parser.add_argument('--project-ids', '-p', dest='project_ids', nargs='+', type=str, help='Gitlab project ids')
    parser.add_argument('--gitlab-url', '-g', dest='gitlab_url', type=str, default='https://gitlab.com/api/v4', help='Gitlab url to use, defaults to https://gitlab.com/api/v4')
    parser.add_argument('--gitlab-headers', '-H', dest='gitlab_headers', type=json_dict, help='Gitlab headers, defaults to {"PRIVATE-TOKEN": self.gitlab_token}')
    parser.add_argument('--can-push', '-c', dest='can_push', type=str, default='true', help='Deploy key write permissions, true or false, defaults to true')
    parser.add_argument('--expires-at', '-x', dest='expire_date', type=str, help='Expiration date of the deploy key to add, defaults to None, (Expected in ISO 8601 format (2019-03-15T08:00:00Z)')
    parser.add_argument('--export', '-e', dest='export_results', action='store_true', help='print results to stdout')
    parser.add_argument('--recursive', '-r', dest='recursive', action='store_true', help='get projects recursively through subgroups')
    parser.add_argument('--remove-by-key', '-D', dest='remove_by_key', action='store_true', help='remove action will remove deploy key based off of ssh key value')
    parser.add_argument("action", choices=["add", "remove"], help="Action to perform: enable or disable")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    gitlab = GitLabAPI(args.gitlab_token, args.group_id, args.project_ids, args.recursive, args.export_results, args.remove_by_key)

    if args.action:
        if args.action == 'add':
            if not args.deploy_key_title:
                args.deploy_key_title = f'Key-{date.today()}'
            data = {"title": args.deploy_key_title, "key": args.deploy_key, "can_push": args.can_push, "expires_at": args.expire_date}
            gitlab.add_deploy_key(args.gitlab_url, data, args.gitlab_headers)
        
        if args.action == 'remove':
            gitlab.remove_deploy_key(args.gitlab_url, args.deploy_key_title, args.deploy_key, args.gitlab_headers)


if __name__ == '__main__':
    main()
