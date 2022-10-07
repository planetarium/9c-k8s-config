import typer
from toolbelt.config import config
from toolbelt.planet.planet import Planet
from toolbelt.types import Network
from toolbelt.utils.typer import network_arg
from .prepare import prepare_release

prepare_app = typer.Typer()


@prepare_app.command()
def release(
    network: str = network_arg,
    tag: str = typer.Argument(...),
    no_create_apv: bool = typer.Argument(False),
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

    planet = Planet(config.key_address, config.key_passphrase)

    return prepare_release(planet, network, rc, no_create_apv)  # type:ignore


__all__ = ["prepare_app"]
