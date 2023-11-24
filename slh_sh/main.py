import typer

import slh_sh.commands.add as add
import slh_sh.commands.extract as extract
import slh_sh.commands.sync as sync

from slh_sh.commands.self import version, list, logs, init
from slh_sh.commands.go import gd, gs, pdf, db, doi
from slh_sh.commands.query import query
from slh_sh.commands.get import info


app = typer.Typer(no_args_is_help=True)

app.add_typer(add.app, name="add")
app.add_typer(extract.app, name="extract")
app.add_typer(sync.app, name="sync")

app.command()(version)
app.command()(query)
app.command()(info)
app.command()(list)
app.command()(logs)
app.command()(init)
app.command()(pdf)
app.command()(doi)
app.command()(gd)
app.command()(gs)
app.command()(db)

if __name__ == "__main__":
    app()
