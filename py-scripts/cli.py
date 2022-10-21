import typer

from toolbelt.prepare import prepare_app
from toolbelt.update import update_app

app = typer.Typer()
app.add_typer(prepare_app, name="prepare")
app.add_typer(update_app, name="update")

if __name__ == "__main__":
    app()
