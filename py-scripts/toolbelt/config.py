import os

from dotenv import load_dotenv
from typing import NamedTuple

config = load_dotenv(".env")

# TODO: need to validation
SLACK_TOKEN: str = os.environ["SLACK_TOKEN"]
GITHUB_TOKEN: str = os.environ["GITHUB_TOKEN"]
KEY_PASSPHRASE: str = os.environ["KEY_PASSPHRASE"]
KEY_ADDRESS: str = os.environ["KEY_ADDRESS"]


class Config(NamedTuple):
    # Slack Bot API Token
    slack_token: str
    # Github token (commit, read)
    github_token: str
    # signer key passphrase
    key_passphrase: str
    # signer key address
    key_address: str


config = Config(
    slack_token=SLACK_TOKEN,
    github_token=GITHUB_TOKEN,
    key_passphrase=KEY_PASSPHRASE,
    key_address=KEY_ADDRESS,
)
