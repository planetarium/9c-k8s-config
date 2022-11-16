from toolbelt.client import DockerClient

namespace = "planetariumhq"
repo = "ninechronicles-headless"
tag = "v100320"


def test_check_image(requests_mock, docker_check_image_exists_sample):
    client = DockerClient(namespace)

    requests_mock.get(
        f"/v2/namespaces/{namespace}/repositories/{repo}/tags/{tag}",
        json=docker_check_image_exists_sample,
    )

    resp = client.check_image_exists(repo, tag)

    assert (
        resp["digest"]
        == "sha256:d6078671858dd40d04614491b32f3beb05c7809edeb844f8f4fcafddb2e3fbb2"
    )
