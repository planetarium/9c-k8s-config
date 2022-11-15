import typer

from toolbelt.check.image import check_headless_image
from toolbelt.utils.typer import network_arg


check_app = typer.Typer()


@check_app.command()
def headless_image(
        network: str = network_arg,
        tag: str = typer.Argument(...)
):
    network_prefix = ""
    if network != "main":
        network_prefix = f"{network}-"

    if not tag.startswith(network_prefix):
        raise ValueError(
            f"Wrong tag, input: {tag}, " f"should be startswith: {network_prefix}"
        )
    try:
        try:
            removed_network = tag.split(network_prefix)[1]
        except ValueError:
            removed_network = tag

        rc = int(removed_network.split("-")[0].lstrip("v"))
    except (IndexError, TypeError, ValueError):
        raise ValueError(f"Wrong tag, input: {tag}")
    return check_headless_image(network, rc)


__all__ = ["headless_image"]
