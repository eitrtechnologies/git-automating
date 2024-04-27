# git-automating

This script helps you manage GitLab deploy keys for projects. 

## Description

This script provides the ability to add or remove deploy keys for GitLab projects within a group or specific project (or list of projects). It introduces functionaility akin to a "group level" deploy key feature within GitLab's current framework.

The script achieves this by taking the group ID (or project ID) as input and traversing the group for projects, then applying or removing the given deploy key accordingly at the project level. Based on input, the script can look recursively through subgroups, or just apply deploy keys to a single project or list of projects directly.

## Actions

The script supports two actions:

* `add`: Adds a deploy key 
* `remove`: Removes a deploy key 

## Usage

### Adding a Deploy Key

**Required Parameters:**

* `deploy-key` (`-d`): The public key of the deploy key to add.
* `gitlab-token` (`-t`):  Your GitLab access token (for authentication with Gitlab API). You can also use the `GITLAB_TOKEN` environment variable.
* `group-id` (`-i`) or `project-id` (`-p`):  The GitLab group ID or project ID (multiple project IDs can be passed).

**Optional Parameters:**

* `export` (`-e`): Prints the response from the GitLab API, project name, and script action to the console for each deploy key.
* `deploy-key-name` (`-n`): The name of the deploy key to add (defaults to `Key-YYYY-MM-DD`).
* `can-push` (`-c`):  Set deploy key write permissions (defaults to `true`).
* `gitlab-url` (`-g`):  Set the GitLab API URL (defaults to `https://gitlab.com/api/v4`).
* `gitlab-headers` (`-H`):  Set GitLab API headers (defaults to `{"PRIVATE-TOKEN": <gitlab_token>}`).
* `recursive` (`-r`): Include subgroups within a group.


**Example Add**

```
git-deploy-key.py add -er -n test -t <gitlab-auth-token> -d "ssh-rsa AAAA..." -i 12345
```

**Example Add with Multiple Project IDs**

```
git-deploy-key.py add -er -n test -t <gitlab-auth-token> -d "ssh-rsa AAAA..." -p 45678 87542
```

### Using Environment Vars
---
To use environment variables, export your GitLab authentication token and/or the GitLab deploy key that you want to add or remove from your projects:

```
export GITLAB_TOKEN="super-secret-gitlab-auth-key"
export GITLAB_DEPLOY_KEY="ssh-rsa AAAA..."
```

**Example Running Script with Environment Vars**

```
git-deploy-key.py add -er -n test -i 12345
```
---

### Removing a deploy key

* `deploy-key-name` (`-n`): The name of the deploy key to remove
* `gitlab-token` (`-t`):  Your GitLab access token (for authentication with Gitlab API). You can also use the `GITLAB_TOKEN` environment variable.
* `group-id` (`-i`) or `project-id` (`-p`):  The GitLab group ID or project ID (multiple project IDs can be passed).

**Optional Parameters:**

* `export` (`-e`): Prints the response from the GitLab API, project name, and script action to the console for each deploy key.
* `can-push` (`-c`):  Set deploy key write permissions (defaults to `true`).
* `gitlab-url` (`-g`):  Set the GitLab API URL (defaults to `https://gitlab.com/api/v4`).
* `gitlab-headers` (`-H`):  Set GitLab API headers (defaults to `{"PRIVATE-TOKEN": <gitlab_token>}`).
* `recursive` (`-r`): Include subgroups within a group.

**Example Remove**

```
git-deploy-key.py remove -er -n test -t <gitlab-auth-token> -i 12345
```

## All Options

| Option (Short Flag) | Long Flag | Description | Default Value |
|---|---|---|---|
| -n | --deploy-key-name | GitLab deploy key name. | Key-YYYY-MM-DD |
| -d | --deploy-key | GitLab deploy key ID. | GITLAB_DEPLOY_KEY environment variable or None |
| -t | --gitlab-token | GitLab access token. | GITLAB_TOKEN environment variable or None |
| -i | --group-id | GitLab group ID. | - |
| -p | --project-id | GitLab project ID. | - |
| -g | --gitlab-url | GitLab API URL. | [https://gitlab.com/api/v4](https://gitlab.com/api/v4) |
| -H | --gitlab-headers | GitLab API headers. | {"PRIVATE-TOKEN": <gitlab_token>} |
| -c | --can-push | Deploy key write permissions. | true |
| -e | --export | Print response from GitLab API, project name, and script action. | - |
| -r | --recursive | Include subgroups within a group. | - |

## Note:

- If --export (-e) is not included as an arg when executing the script, a successful run will not print anything to the console. However, if an error is hit during executing a log message will still print.
