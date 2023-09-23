import typer
from pathlib import Path
from rich import print


global_config_path: Path = Path.cwd() / "config.yaml"
if global_config_path.is_file():
    import slh.commands.extract as extract
    import slh.commands.get as get
    import slh.commands.add as add
    import slh.commands.go as go
    import slh.commands.sync as sync
    import slh.commands.self as self
else:
    print(
        """
        [bold red]Alert![/bold red]

        Config file does not exist in current directory.

        Run [yellow]slh init[/yellow] to create one :rocket:
        """
    )


app = typer.Typer()


if global_config_path.is_file():
    app.add_typer(extract.app, name="extract")
    app.add_typer(get.app, name="get")
    app.add_typer(add.app, name="add")
    app.add_typer(go.app, name="go")
    app.add_typer(sync.app, name="sync")
    app.add_typer(self.app, name="self")


if __name__ == "__main__":
    app()
