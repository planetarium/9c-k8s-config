from typing import Dict

import requests

DOCKER_HUB_URL = "https://hub.docker.com"


class DockerClient:
    def __init__(self, username: str, password: str, *, namespace: str) -> None:
        self._username = username
        self._password = password
        self._namespace = namespace
        self._token = ""
        self.login()

    def login(self):
        resp = requests.post(
            f"{DOCKER_HUB_URL}/v2/users/login/",
            data={"username": self._username, "password": self._password}
        )
        try:
            token = resp.json()["token"]
        except KeyError:
            raise ValueError("docker hub login failed")
        self._token = token

    def check_image_exists(self, repo: str, tag: str):
        resp = requests.get(
            f"{DOCKER_HUB_URL}/v2/namespaces/{self._namespace}/repositories/{repo}/tags/{tag}",
            headers={"Authorization": f"Bearer {self._token}"}
        )
        if resp.status_code != 200:
            raise ValueError(f"Docker image for tag {tag} not in the repository {repo}")

