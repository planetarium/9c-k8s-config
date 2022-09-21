## Prerequisite

**.env**
- GITHUB_TOKEN: 1password k8s-github-token or your github token(required org:read permission)
- SLACK_TOKEN: 1password Slack Token

**boto3**
- aws_access_key_id, aws_secret_access_key: $aws configure (~/.aws/credentials)

Installation

- required [planet](https://www.npmjs.com/package/@planetarium/cli)

**Python**
```python
# cd ./py-scripts
$ python -m venv .venv
$ . .venv/bin/activate
$ pip install -r requirements.txt
```

## Usage

**Run --help**

```bash
python cli.py --help
```

### for internal

```bash
$ python cli.py prepare internal_test <APV version (e.g. v100086)> 
$ git checkout -t origin/v100086
$ sh ../9c-internal/deploy-internal.sh
```

### for main

```bash
$ python cli.py prepare deploy-main <APV version (e.g. v100086)>
$ git checkout -t origin/v100086
$ sh ../9c-main/deploy-main.sh
$ python cli.py update post-deploy <APV version (e.g. v100086)>
```
