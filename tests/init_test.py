from typer.testing import CliRunner

from slh.main import app

runner = CliRunner()


# write test for commands/init.py
def test_init():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Init..." in result.output
