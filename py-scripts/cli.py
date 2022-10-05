import typer
from toolbelt.prepare import prepare_main_deploy
from toolbelt.update.post_deploy import update_post_deploy
from toolbelt.prepare import release_app
from toolbelt.utils.typer import version_arg, apv_arg

prepare_app = typer.Typer()


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


app = typer.Typer()
app.add_typer(prepare_app, name="prepare")
app.add_typer(update_app, name="update")
app.add_typer(release_app, name="release")

if __name__ == "__main__":
    app()
