from typing import Optional

import typer

from toolbelt.utils.typer import network_arg

from .prepare import prepare_release

prepare_app = typer.Typer()


@prepare_app.command()
def release(
    network: str = network_arg,
    rc: int = typer.Argument(...),
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
            f"Wrong tag, input: {tag}, " f"should be startswith: {network_prefix}"
        )
    return prepare_release(
        network, rc, slack_channel=slack_channel  # type:ignore
    )


__all__ = ["prepare_app"]
