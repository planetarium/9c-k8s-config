from dataclasses import dataclass
from typing import Callable, Dict, List, Union

import validate_docker as docker

import toolbelt.client.notion as notion
import toolbelt.github.old_github as old_github


@dataclass(frozen=True)
class SuccessValidationResult:
    name: str


@dataclass(frozen=True)
class InvalidValidationResult:
    name: str
    reason: str


ValidationResult = Union[SuccessValidationResult, InvalidValidationResult]


def validate_statefulset_or_deployment(
    conf: dict, release_note: notion.ReleaseNote
) -> List[ValidationResult]:
    results: List[ValidationResult] = []
    containers: List[dict] = conf["spec"]["template"]["spec"]["containers"]
    for container in containers:
        valid, reason = docker.validate_container(container, release_note)
        if valid:
            results.append(SuccessValidationResult(container["name"]))
        else:
            results.append(InvalidValidationResult(container["name"], reason))

    return results


def validate_cronjob(
    conf: dict, release_note: notion.ReleaseNote
) -> List[ValidationResult]:
    results: List[ValidationResult] = []
    template = conf["spec"]["jobTemplate"]["spec"]["template"]["spec"]
    init_containers = template["initContainers"]
    containers = template["containers"]
    for container in init_containers:
        valid, reason = docker.validate_container(container, release_note)
        if valid:
            results.append(SuccessValidationResult(container["name"]))
        else:
            results.append(InvalidValidationResult(container["name"], reason))

    for container in containers:
        valid, reason = docker.validate_container(container, release_note)
        if valid:
            results.append(SuccessValidationResult(container["name"]))
        else:
            results.append(InvalidValidationResult(container["name"], reason))

    return results


_VALIDATOR_MAP: Dict[str, Callable[[dict, notion.ReleaseNote], List[ValidationResult]]]


def validate_list(
    conf: dict, release_note: notion.ReleaseNote
) -> List[ValidationResult]:
    results: List[ValidationResult] = []
    for conf in conf["items"]:
        kind: str = conf["kind"]
        results += _VALIDATOR_MAP[kind](conf, release_note)

    return results


_VALIDATOR_MAP = {
    "Deployment": validate_statefulset_or_deployment,
    "StatefulSet": validate_statefulset_or_deployment,
    "CronJob": validate_cronjob,
    "List": validate_list,
}


if __name__ == "__main__":
    import argparse

    import yaml

    parser = argparse.ArgumentParser()
    parser.add_argument("pull_request_number", metavar="PULL_REQUEST_NUMBER", type=int)
    parser.add_argument("release_version", metavar="RELEASE_VERSION", type=str)

    args = parser.parse_args()

    _pull_request_number = args.pull_request_number
    _release_version = args.release_version

    _head = old_github.get_pull_request_head("9c-k8s-config", _pull_request_number)
    _release_note = notion.get_release_note(_release_version)

    nc_main_configuration_files = (
        "full-state.yaml",
        "headless.yaml",
        "explorer.yaml",
        "data-provider.yaml",
        "snapshot.yaml",
        "snapshot-partition.yaml",
        *[f"miner-{i}.yam" for i in range(1, 5)],
        *map(lambda x: f"seed-deployment-{x}.yaml", range(1, 4)),
    )

    for configuration_file in map(
        lambda x: f"9c-main/{x}", nc_main_configuration_files
    ):
        sha, content = old_github.get_path_content(
            "9c-k8s-config", configuration_file, _head["sha"]
        )
        for _conf in yaml.safe_load_all(content):
            _kind = _conf["kind"]
            print(
                _VALIDATOR_MAP[_kind](_conf, _release_note),
                "in",
                configuration_file,
            )
