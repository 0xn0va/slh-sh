from slh.config import load_config
import typer
from typing_extensions import Annotated
from rich import print

app = typer.Typer()
configData = load_config()


@app.command()
def check():
    print("Check...")


@app.command()
def update():
    print("Update...")


@app.command()
def backup():
    print("Backup...")


@app.command()
def restore():
    print("Restore...")


@app.command()
def logs():
    print("Logs...")


@app.command()
def list():
    print("List all commands...")
