import typer
from toolbelt.update.post_deploy import update_post_deploy
from toolbelt.prepare import prepare_app
from toolbelt.utils.typer import version_arg


update_app = typer.Typer()


@update_app.command()
def post_deploy(version: str = version_arg):
    """
    Run post deploy script
    """

    return update_post_deploy(version)


app = typer.Typer()
app.add_typer(prepare_app, name="prepare")
app.add_typer(update_app, name="update")

if __name__ == "__main__":
    app()
