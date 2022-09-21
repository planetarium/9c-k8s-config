import os
from dotenv import load_dotenv

config = load_dotenv()

# Very simple validation
try:
    SLACK_TOKEN: str = os.environ["SLACK_TOKEN"]  # type:ignore
    GITHUB_TOKEN: str = os.environ["GITHUB_TOKEN"]  # type:ignore
    INTERNAL_PASSPHRASE: str = os.environ["INTERNAL_PASSPHRASE"]  # type:ignore
    INTERNAL_ADDRESS: str = os.environ["INTERNAL_ADDRESS"]  # type:ignore
    MAINNET_PASSPHRASE: str = os.environ["MAINNET_PASSPHRASE"]  # type:ignore
    MAINNET_ADDRESS: str = os.environ["MAINNET_ADDRESS"]  # type:ignore
except KeyError:
    raise KeyError("Please create .env file")
