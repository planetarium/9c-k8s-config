import time
import base64
from typing import Any, Iterator

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
        """
        It takes a response object from the requests library,
        checks for errors, and returns the JSON response

        :param r: requests.Response
        :type r: requests.Response
        :return: json response
        """

        r.raise_for_status()
        res = r.json()

        return res

    def get_tags(
        self, *, offset: int = 1, per_page: int = 10
    ) -> Iterator[Any]:
        """
        It returns a generator that yields a list of tags for a given repo.

        :param offset: The page number to start on, defaults to 1
        :type offset: int (optional)
        :param per_page: The number of items to return per page, defaults to 10
        :type per_page: int (optional)
        """

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

    def get_path_content(self, path: str, branch: str):
        params = {"ref": branch}

        r = self._session.get(
            f"/repos/{self.org}/{self.repo}/contents/{path}", params=params
        )
        print(r)
        response = self.handle_response(r)

        content = (
            base64.b64decode(response["content"]).decode("utf-8")
            if "content" in response
            else None
        )

        return content, response
