import time

import requests

from toolbelt.client.session import BaseUrlSession

GITHUB_BASE_URL = "https://api.github.com"


class GithubClient:
    def __init__(self, token: str, *, org: str, repo: str) -> None:
        """
        GithubClient implementation with github rest api.
        [https://docs.github.com/en/rest]

        :param token: The token of the bot
        :type token: str
        """

        self._token = token
        self._session = BaseUrlSession(GITHUB_BASE_URL)

        self._session.headers.update({"Authorization": f"token {token}"})

        self.org = org
        self.repo = repo

    def handle_response(self, r: requests.Response):
        r.raise_for_status()
        res = r.json()

        return res

    def get_tags(self, *, offset: int = 1, per_page: int = 10):
        # Max page hard coding(100)
        for page in range(offset, 100):
            params = {
                "per_page": per_page,
                "page": page,
            }
            r = self._session.get(
                f"/repos/{self.org}/{self.repo}/tags", params=params
            )
            response = self.handle_response(r)
            if len(response) == 0:
                break

            yield response

            # Temp delay
            time.sleep(1)
