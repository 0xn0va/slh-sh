import typer

import slh_sh.commands.extract as extract
import slh_sh.commands.get as get
import slh_sh.commands.add as add
import slh_sh.commands.go as go
import slh_sh.commands.sync as sync
import slh_sh.commands.self as self

app = typer.Typer()

app.add_typer(extract.app, name="extract")
app.add_typer(get.app, name="get")
app.add_typer(add.app, name="add")
app.add_typer(go.app, name="go")
app.add_typer(sync.app, name="sync")
app.add_typer(self.app, name="self")

if __name__ == "__main__":
    app()
