import os

from dotenv import load_dotenv

config = load_dotenv()

# Very simple validation
try:
    SLACK_TOKEN: str = os.environ["SLACK_TOKEN"]  # type:ignore
    GITHUB_TOKEN: str = os.environ["GITHUB_TOKEN"]  # type:ignore
    KEY_PASSPHRASE: str = os.environ["KEY_PASSPHRASE"]  # type:ignore
    KEY_ADDRESS: str = os.environ["KEY_ADDRESS"]  # type:ignore
except KeyError:
    raise KeyError("Please create .env file")
