import typer

from toolbelt.check.image import check_headless_image
from toolbelt.utils.typer import network_arg

check_app = typer.Typer()


@check_app.command()
def headless_image(
    network: str = network_arg,
    rc_number: int = typer.Argument(...),
    deploy_number: int = typer.Argument(...),
):
    return check_headless_image(
        network,  # type:ignore
        rc_number,
        deploy_number,
    )


__all__ = ["headless_image"]
