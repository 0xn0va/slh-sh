import typer
import sys

from pathlib import Path
from rich import print


config: Path = Path.cwd() / "config.yaml"
if config.is_file():
    import slh_sh.commands.extract as extract
    import slh_sh.commands.get as get
    import slh_sh.commands.add as add
    import slh_sh.commands.go as go
    import slh_sh.commands.sync as sync
    import slh_sh.commands.self as self
else:
    print(
        """
        [bold green]Good day researcher :wave:[/bold green]

        The [red]config.yaml[/red] file does not exist in the current directory.

            - Run [yellow]slh self init[/yellow] to initialize a new SLR project :rocket:
            - [blue]https://github.com/xN0Vx/slh[/blue]
        """
    )
    sys.exit(1)


app = typer.Typer()


app.add_typer(extract.app, name="extract")
app.add_typer(get.app, name="get")
app.add_typer(add.app, name="add")
app.add_typer(go.app, name="go")
app.add_typer(sync.app, name="sync")
app.add_typer(self.app, name="self")


if __name__ == "__main__":
    app()
