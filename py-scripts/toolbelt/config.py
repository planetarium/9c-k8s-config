import os
from typing import NamedTuple, get_args

from dotenv import load_dotenv

from toolbelt.types import Env

load_dotenv(".env")

# TODO: need to validation
_env: str = os.environ["ENV"]
slack_token: str = os.environ["SLACK_TOKEN"]
github_token: str = os.environ["GITHUB_TOKEN"]
key_passphrase: str = os.environ["KEY_PASSPHRASE"]
key_address: str = os.environ["KEY_ADDRESS"]


class Config(NamedTuple):
    # Slack Bot API Token
    slack_token: str
    # Github token (commit, read)
    github_token: str
    # signer key passphrase
    key_passphrase: str
    # signer key address
    key_address: str
    # env
    env: Env = "test"


env_map = {v: v for v in get_args(Env)}
try:
    env = env_map[_env]
except KeyError:
    raise ValueError(f"Env should in {get_args(Env)}")


config = Config(
    env=env,
    slack_token=slack_token,
    github_token=github_token,
    key_passphrase=key_passphrase,
    key_address=key_address,
)
