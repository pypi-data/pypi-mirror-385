import typer
from ...registry.docker import DockerRegistry

app = typer.Typer(add_completion=False)


@app.command()
def login(name, registry, username, password):
    DockerRegistry(registry).login(nmae=name, username=username, password=password)


@app.command()
def push(registry: str, image: str):
    DockerRegistry(registry).push(image)


@app.command()
def pull(registry: str, image: str):
    DockerRegistry(registry).pull(image)
