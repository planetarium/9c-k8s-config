import typer
from typing import Optional
from toolbelt.prepare import prepare_main_deploy
from toolbelt.update import update_post_deploy
from toolbelt.v2.command import internal_release

prepare_app = typer.Typer()


def version_validation(ctx: typer.Context, p: typer.CallbackParam, v: str):
    if ctx.resilient_parsing:
        return
    if len(v) != 7 or not v.startswith("v"):
        raise typer.BadParameter("APV version (e.g. v100086)")
    return v


version_arg = typer.Argument(
    ..., help="RC version ie. v100260", callback=version_validation
)
apv_arg = typer.Argument(..., help="APV version ie. 1085/123...")


@prepare_app.command()
def deploy_main(version: str = version_arg, apv: str = apv_arg):
    """
    Prepare deploy mainnet\n
    Required `GITHUB_TOKEN` in .env file
    """

    return prepare_main_deploy(version, apv)


update_app = typer.Typer()


@update_app.command()
def post_deploy(version: str = version_arg):
    """
    Run post deploy script
    """

    return update_post_deploy(version)


release_app = typer.Typer()


@release_app.command()
def internal(version: str = typer.Argument(...)):
    """
    Run internal release script
    """

    return internal_release(version)


app = typer.Typer()
app.add_typer(prepare_app, name="prepare")
app.add_typer(update_app, name="update")
app.add_typer(release_app, name="release")

if __name__ == "__main__":
    app()
