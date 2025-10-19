import typer

from easyfederated.cli.commands.start import start as start_impl
from easyfederated.cli.commands.status import status as status_impl
from easyfederated.cli.commands.stop import stop as stop_impl
from easyfederated.cli.commands.clean import clean as clean_impl

app = typer.Typer()


@app.command()
def start():
    start_impl(path="./examples/fake_project/easyfed.yaml")


@app.command()
def status():
    status_impl(path="./examples/fake_project/easyfed.yaml")


@app.command()
def stop():
    stop_impl(path="./examples/fake_project/easyfed.yaml")


@app.command()
def clean():
    clean_impl(path="./examples/fake_project/easyfed.yaml")
