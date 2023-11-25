import typer

import slh_sh.commands.add as add
import slh_sh.commands.extract as extract
import slh_sh.commands.sync as sync

from slh_sh.commands.self import version, list, logs, init, check
from slh_sh.commands.go import gd, gs, pdf, db, doi
from slh_sh.commands.query import query
from slh_sh.commands.get import info
from slh_sh.utils.log import logger


app = typer.Typer(
    no_args_is_help=True, rich_markup_mode="rich", epilog="Made with [red]:heart:[/red]"
)

app.add_typer(add.app, name="add")
app.add_typer(extract.app, name="extract")
app.add_typer(sync.app, name="sync")

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
app.command(rich_help_panel="Data")(info)
app.command(rich_help_panel="Data")(query)


if __name__ == "__main__":
    app()
