import typer
from toolbelt.types import Network
from .prepare import prepare_release

prepare_app = typer.Typer()


@prepare_app.command()
def release(
    network: Network = typer.Argument(...), tag: str = typer.Argument(...)
):
    """
    Run internal release script
    """

    return prepare_release(network, tag)


__all__ = ["prepare_app"]
