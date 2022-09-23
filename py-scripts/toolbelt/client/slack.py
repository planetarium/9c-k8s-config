import requests


class SlackClient:
    def __init__(self, token: str) -> None:
        """
        It creates a new instance of the class, and sets the token and session attributes

        :param token: The token of the bot
        :type token: str
        """

        self._token = token

        self.session = requests.Session()

    @property
    def token(self):
        """
        It returns the token.
        :return: The token is being returned.
        """

        return self._token

    def post_msg(self, msg: str, *, channel: str):
        pass
