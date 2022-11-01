## Prerequisite

**.env**
- GITHUB_TOKEN: 1password k8s-github-token or your github token(required org:read permission)
- SLACK_TOKEN: 1password Slack Token

**boto3**
- aws_access_key_id, aws_secret_access_key: $aws configure (~/.aws/credentials)

**Installation**
- required [planet](https://www.npmjs.com/package/@planetarium/cli)

**Python**
```python
# cd ./py-scripts
$ python -m venv .venv
$ . .venv/bin/activate
$ pip install -r requirements-dev.txt
$ flit install --extras all
```

## Usage

**Run --help**

```bash
python cli.py --help
```

### Prepare Release

```bash
$ python cli.py prepare release internal <tag>
```

### Post Deploy

```bash
$ python cli.py update release-infos
```
