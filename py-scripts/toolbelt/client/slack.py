from typing import List

from toolbelt.exceptions import ResponseError

from .session import BaseUrlSession

SLACK_BASE_URL = "https://slack.com"


class SlackClient:
    def __init__(self, token: str) -> None:
        """
        It creates a new instance of the class, and sets the token and session attributes

        :param token: The token of the bot
        :type token: str
        """

        self._token = token
        self._session = BaseUrlSession(SLACK_BASE_URL)

        self._session.headers.update({"Authorization": f"Bearer {self.token}"})

    @property
    def token(self):
        """
        It returns the token.
        :return: The token is being returned.
        """

        return self._token

    def send_simple_msg(self, channel: str, msg: str):
        return self.send_msg(channel, text=msg)

    def send_msg(
        self,
        channel: str,
        *,
        text: str,
        blocks: List[str] = [],
        attachments: List[str] = [],
    ):
        r = self._session.post(
            "/api/chat.postMessage",
            data={
                "channel": channel,
                "text": text,
                "blocks": blocks,
                "attachments": attachments,
            },
        )

        r.raise_for_status()

        response = r.json()

        if not response["ok"]:
            raise ResponseError(f"SlackAPI ResponseError: body: {response}")

        return response
