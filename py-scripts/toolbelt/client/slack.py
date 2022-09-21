# https://pypi.org/project/slack-sdk/

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from toolbelt.config import SLACK_TOKEN

client = WebClient(token=SLACK_TOKEN, timeout=300)


def send_message(channel, text):
    try:
        response = client.chat_postMessage(channel=f"#{channel}", text=text)
        assert response["message"]["text"] == text
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response[
            "error"
        ]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")


def upload_file(channel, filepath):
    try:
        response = client.files_upload(channels=f"#{channel}", file=filepath)
        assert response["file"]  # the uploaded file
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response[
            "error"
        ]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")


if __name__ == "__main__":
    _channel = "9c-internal"
    _message = "[K8S] test message"
    send_message(_channel, _message)

    _filepath = "requirements.txt"
    upload_file(_channel, _filepath)
