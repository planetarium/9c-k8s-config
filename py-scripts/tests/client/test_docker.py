from toolbelt.client import DockerClient

DOCKER_HUB_URL = "https://hub.docker.com"

namespace = "planetariumhq"
repo = "ninechronicles-headless"
tag = "v100321"


def test_check_image(requests_mock):
    client = DockerClient(namespace)

    requests_mock.get(
        f"/v2/namespaces/{namespace}/repositories/{repo}/tags/{tag}"
    )

    assert client.check_image_exists(repo, tag)
