import typer

from pathlib import Path
from rich import print

import slh_sh.commands.add as add
import slh_sh.commands.extract as extract
import slh_sh.commands.sync as sync

from slh_sh.commands.self import version, list, logs, init, check
from slh_sh.commands.go import gd, gs, pdf, db, doi
from slh_sh.commands.query import query
from slh_sh.commands.get import info


app = typer.Typer(
    no_args_is_help=True, rich_markup_mode="rich", epilog="Made with [red]:heart:[/red]"
)

app.add_typer(add.app, name="add", rich_help_panel="Database Import")
app.add_typer(extract.app, name="extract", rich_help_panel="Data Extraction")
app.add_typer(sync.app, name="sync", rich_help_panel="Sheet to Database Syncronization")

app.command(rich_help_panel="slh-sh")(version)
app.command(rich_help_panel="slh-sh")(list)
app.command(rich_help_panel="slh-sh")(logs)
app.command(rich_help_panel="slh-sh")(init)
app.command(rich_help_panel="slh-sh")(check)
app.command(rich_help_panel="Shortcuts")(pdf)
app.command(rich_help_panel="Shortcuts")(doi)
app.command(rich_help_panel="Shortcuts")(gd)
app.command(rich_help_panel="Shortcuts")(gs)
app.command(rich_help_panel="Shortcuts")(db)
app.command(rich_help_panel="Data Query")(info)
app.command(rich_help_panel="Data Query")(query)


@app.callback()
def callback(ctx: typer.Context):
    """
    slh-sh is a command line tool to manage systematic literature reviews.
    """
    config_path = Path.cwd() / "config.yaml"
    if config_path.exists():
        pass
    else:
        print(
            """
[bold green]Good day researcher :wave:[/bold green]

The [red]config.yaml[/red] file does not exist in the current directory.

    - Run [yellow]slh-sh init[/yellow] to initialize a new SLR project :rocket:
            """
        )


if __name__ == "__main__":
    app()
