import requests
import logging
import argparse
from datetime import date
import json

log = logging.getLogger(__name__)


class GitLabAPI:

    def __init__(self, gitlab_token, group_id, export_results):
        self.gitlab_token = gitlab_token
        self.group_id = group_id
        self.export_results = export_results

    def _make_request(self, url, method='GET', headers=None, data=None):
        if not headers:
            headers = {"PRIVATE-TOKEN": self.gitlab_token}
        try:
            response = requests.request(method, url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.error("Error fetching from Gitlab API: %s", e)
            return {}

        try:
            return response.json()
        except ValueError:
            return response


    def _list_projects(self, url, headers=None):
        url = f"{url}/groups/{self.group_id}/projects"
        projects = self._make_request(url, headers=headers)
        return projects


    def add_deploy_key(self, url, data, headers=None):
        projects = self._list_projects(url, headers)

        for project in projects:
            url = f"{url}/projects/{project['id']}/deploy_keys"
            response = self._make_request(url, method='POST', headers=headers, data=data)
            self._export_results(response, "add", project['name'])


    def remove_deploy_key(self, url, deploy_key_title, headers=None):
        projects = self._list_projects(url, headers)

        for project in projects:
            _url = f"{url}/projects/{project['id']}/deploy_keys"
            deploy_keys = self._make_request(_url, headers=headers)

            for key in deploy_keys:
                if key['title'] == deploy_key_title:
                    _url = f"{url}/projects/{project['id']}/deploy_keys/{key['id']}"
                    response = self._make_request(_url, method='DELETE', headers=headers)
                    self._export_results(response, "remove", project['name'])


    def _export_results(self, response, action, project):
        if self.export_results:
            print(f"{action}: {project}: {response}")


def json_dict(value):
    try:
        return json.loads(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f'Invalid JSON: {e}')
    

def main():

    # Set commandline args
    parser = argparse.ArgumentParser(description='Utility script to enable or disable deploy key for projects in a GitLab group')

    parser.add_argument('--deploy-key-name', '-n', dest='deploy_key_title', type=str, default=f'Key-{date.today()}', help='Gitlab deploy key name, defaults to Key-YYYY-MM-DD')
    parser.add_argument('--deploy-key', '-d', dest='deploy_key', type=str, help='Gitlab deploy key id')
    parser.add_argument('--gitlab-token', '-t', dest='gitlab_token', type=str, help='Gitlab token')
    parser.add_argument('--group-id', '-i', dest='group_id', type=int, help='Gitlab group id')
    parser.add_argument('--gitlab-url', '-g', dest='gitlab_url', type=str, default='https://gitlab.com/api/v4', help='Gitlab url to use, defaults to https://gitlab.com/api/v4')
    parser.add_argument('--gitlab-headers', '-H', dest='gitlab_headers', type=json_dict, help='Gitlab headers, defaults to {"PRIVATE-TOKEN": self.gitlab_token}')
    parser.add_argument('--can-push', '-c', dest='can_push', type=str, default='true', help='Deploy key write permissions, true or false, defaults to true')
    parser.add_argument('--export', '-e', dest='export_results', action='store_true', help='print results to stdout')
    parser.add_argument("action", choices=["add", "remove"], help="Action to perform: enable or disable")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    if not args.gitlab_token or not args.group_id:
        log.error("Missing required parameters: gitlab_token or group_id")

    gitlab = GitLabAPI(args.gitlab_token, args.group_id, args.export_results)

    if args.action:
        if args.action == 'add':
            data = {"title": args.deploy_key_title, "key": args.deploy_key, "can_push": args.can_push}
            gitlab.add_deploy_key(args.gitlab_url, data, args.gitlab_headers)
        
        if args.action == 'remove':
            gitlab.remove_deploy_key(args.gitlab_url, args.deploy_key_title, args.gitlab_headers)


if __name__ == '__main__':
    main()
