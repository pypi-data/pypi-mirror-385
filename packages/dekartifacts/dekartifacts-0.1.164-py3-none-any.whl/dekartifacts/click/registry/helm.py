import typer
from typing_extensions import Annotated
from dektools.web.url import Url
from ...registry.helm import HelmRegistry

app = typer.Typer(add_completion=False)


@app.command()
def login(
        name,
        registry,
        username: Annotated[str, typer.Argument()] = "",
        password: Annotated[str, typer.Argument()] = ""):
    url = Url.new(registry)
    username = url.username or username
    password = url.password or password
    HelmRegistry(registry).login(name=name, username=username, password=password)


@app.command()
def logoff(registry: str):
    HelmRegistry(registry).logoff()


@app.command()
def push(registry: str, path: str):
    HelmRegistry(registry).push(path)


@app.command()
def pull(registry: str, path: str):
    HelmRegistry(registry).pull(path)
