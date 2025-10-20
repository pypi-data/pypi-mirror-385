from dektools.typer import command_version
from . import app
from .image import app as image_app
from .registry.docker import app as docker_app
from .registry.helm import app as helm_app
from .registry.staticfiles import app as staticfiles_app

command_version(app, __name__)
app.add_typer(image_app, name='image')
app.add_typer(docker_app, name='docker')
app.add_typer(helm_app, name='helm')
app.add_typer(staticfiles_app, name='staticfiles')


def main():
    app()
