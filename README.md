# git-automating

Utility script for managing GitLab deploy keys at the group level

## Action

`add`: Adds a deploy key across all projects included in a group\
`remove`: Removes a deploy key across all projects included in a group

## Usage

### Adding a deploy key

To add a deploy key, the following parameters are required:

- deploy-key _(-d)_ - the public key of the deploy key to add
- gitlab-token _(-t)_ - your Gitlab auth token (for authentication with Gitlab API)
- group-id _(-i)_ - the Gitlab group id 

optional parameters to consider when using the add functionality:

- export _(-e)_ - prints to stdout the response from the Gitlab API, project name, and script action (add) for each added deploy key
- deploy-key-name _(-n)_ - the name of the deploy key to add (defaults to Key-YYYY-MM-DD)
- can-push _(-c)_ - deploy key write permissions (defaults to true)
- gitlab-url _(-g)_ - Gitlab API URL (defaults to https://gitlab.com/api/v4)
- gitlab-headers (-H) - Gitlab API headers (defaults to `{"PRIVATE-TOKEN": <gitlab_token>}`)

__Example:__

```
python git-deploy-key.py add -e -n test -t <your-token> -d "ssh-rsa AAAA..." -i 123
```

_or_

```
python git-deploy-key.py add --export --gitlab-token <your-token> --deploy-key-name test --deploy-key "ssh-rsa AAAA..." --group-id 123
```


### Removing a deploy key

To remove a deploy key, the following parameters are required:

- deploy-key-name _(-n)_ - the name of the deploy key to add
- gitlab-token _(-t)_ - your Gitlab auth token (for authentication with Gitlab API)
- group-id _(-i)_ - the Gitlab group id 

optional parameters to consider when using the remove functionality:

- export _(-e)_ - prints to stdout the response from the Gitlab API, project name, and script action (remove) for each removed deploy key 
- gitlab-url _(-g)_ - Gitlab API URL (defaults to https://gitlab.com/api/v4)
- gitlab-headers _(-H)_ - Gitlab API headers (defaults to {"PRIVATE-TOKEN": <gitlab_token>})

__Example__:

```
python git-deploy-key.py remove -e -n test -t <your-token> -t "ssh-rsa AAAA..." -i 123
```

_or_

```
python git-deploy-key.py remove --export --deploy-key-name test --gitlab-token <your-token> --group-id 123
```


### All Options:

- deploy-key-name, _-n_: Gitlab deploy key name. Defaults to Key-YYYY-MM-DD.
- deploy-key, _-d_: Gitlab deploy key ID.
- gitlab-token, _-t_: Gitlab access token.
- group-id, _-i_: Gitlab group ID.
- gitlab-url, _-g_: Gitlab API URL. Defaults to https://gitlab.com/api/v4.
- gitlab-headers, _-H_: Gitlab API headers. Defaults to {"PRIVATE-TOKEN": <gitlab_token>}.
- can-push, _-c_: Deploy key write permissions. Defaults to true.
- export, _-e_: prints to stdout the response from the Gitlab API, project name, and script action for each deploy key


## Note:

- If --export (-e) is not included as an arg when executing the script, a successful run will not print anything. However, if an error is hit during executing a log message will still print
