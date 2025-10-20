import typer
from typing_extensions import Annotated
from ...registry.staticfiles import StaticfilesRegistry

app = typer.Typer(add_completion=False)


@app.command()
def login(registry, username, password):
    StaticfilesRegistry(registry).login(username=username, password=password)


@app.command()
def push(registry: str, path: str, version: Annotated[str, typer.Argument()] = ""):
    StaticfilesRegistry(registry).push(path, version=version)


@app.command()
def pull(registry: str, path: str, version: Annotated[str, typer.Argument()] = ""):
    StaticfilesRegistry(registry).pull(path, version=version)
