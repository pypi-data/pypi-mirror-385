import typer
from ...registry.helm import HelmRegistry

app = typer.Typer(add_completion=False)


@app.command()
def login(registry, username, password):
    HelmRegistry(registry).login(username=username, password=password)


@app.command()
def push(registry: str, path: str):
    HelmRegistry(registry).push(path)


@app.command()
def pull(registry: str, path: str):
    HelmRegistry(registry).pull(path)
