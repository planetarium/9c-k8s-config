from typing import Iterator, List, Optional, Tuple, TypedDict
import os
import sys
import yaml


class Env(TypedDict):
    name: str
    value: str


class Container(TypedDict):
    image: str
    args: Optional[str]
    env: Optional[List[Env]]


def discover_configuration_files(directory: str) -> Iterator[str]:
    return (
        os.path.join(directory, path)
        for path in os.listdir(directory)
        if path.endswith(".yaml")
    )


def discover_kubernetes_configurations(directory: str) -> Iterator[Tuple[str, dict]]:
    for configuration_file in discover_configuration_files(directory):
        raw_conf = read_file(configuration_file)
        for conf in yaml.safe_load_all(raw_conf):
            yield configuration_file, conf


def discover_containers(directory: str) -> Iterator[Tuple[str, Container]]:
    for path, kube_conf in discover_kubernetes_configurations(directory):
        if kube_conf.get("kind") == "CronJob":
            for container in kube_conf["spec"]["jobTemplate"]["spec"]["template"][
                "spec"
            ]["containers"]:
                yield path, container
        elif kube_conf.get("kind") == "Deployment":
            for container in kube_conf["spec"]["template"]["spec"]["containers"]:
                yield path, container
        elif kube_conf.get("kind") == "StatefulSet":
            for container in kube_conf["spec"]["template"]["spec"]["containers"]:
                yield path, container


def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def fetch_apv_from_headless(container: Container) -> str:
    args = " ".join(container["args"]).split(" ")
    for arg in args:
        if arg.startswith("--app-protocol-version"):
            return arg.removeprefix("--app-protocol-version=")


def fetch_apv_from_seed(container: Container) -> str:
    args = " ".join(container["args"]).split(" ")
    for arg in args:
        if arg.startswith("--app-protocol-version"):
            return arg.removeprefix("--app-protocol-version=")


def fetch_apv_from_data_provider(container: Container) -> str:
    for env in container["env"]:
        if env["name"] == "NC_AppProtocolVersionToken":
            return env["value"]


_DOCKER_REPO_TO_APV_FETCHER = {
    "planetariumhq/ninechronicles-headless": fetch_apv_from_headless,
    "planetariumhq/libplanet-seed": fetch_apv_from_seed,
    "planetariumhq/ninechronicles-dataprovider": fetch_apv_from_data_provider,
}

if "__main__" == __name__:
    import argparse
    import re

    parser = argparse.ArgumentParser()
    parser.add_argument("PATH", type=str)
    parser.add_argument(
        "--ignore-regex",
        type=str,
        help="The regular expression to specific files which isn't checked by this script.",
    )
    args = parser.parse_args()

    previous_path: Optional[str] = None
    previous_apv: Optional[str] = None

    for path, container in discover_containers(args.PATH):
        if args.ignore_regex and re.findall(args.ignore_regex, path):
            continue

        repo = container["image"].split(":")[0]
        fetcher = _DOCKER_REPO_TO_APV_FETCHER.get(repo)
        if fetcher is not None:
            apv = fetcher(container)
            if previous_apv is not None and apv != previous_apv:
                print(
                    f"They are different between {apv} at {path}, {previous_apv} at {previous_path}",
                    file=sys.stderr,
                )
                exit(-1)
            else:
                previous_apv = apv
                previous_path = path

    print(f"::set-output name=apv::{previous_apv}")
    exit(0)
