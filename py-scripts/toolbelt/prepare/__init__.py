from typing import Optional

import typer

from toolbelt.utils.typer import network_arg

from .prepare import prepare_release

prepare_app = typer.Typer()


@prepare_app.command()
def release(
    network: str = network_arg,
    tag: str = typer.Argument(...),
    slack_channel: Optional[str] = None,
):
    """
    Run internal release script
    """
    network_prefix = ""
    if network != "main":
        network_prefix = f"{network}-"

    if not tag.startswith(network_prefix):
        raise ValueError(
            f"Wrong tag, input: {tag}, "
            f"should be startswith: {network_prefix}"
        )
    try:
        try:
            removed_network = tag.split(network_prefix)[1]
        except ValueError:
            removed_network = tag

        rc = int(removed_network.split("-")[0].lstrip("v"))
    except (IndexError, TypeError, ValueError):
        raise ValueError(f"Wrong tag, input: {tag}")

    return prepare_release(network, rc, slack_channel=slack_channel)


__all__ = ["prepare_app"]
