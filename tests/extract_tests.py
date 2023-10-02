from typer.testing import CliRunner

from slh_sh.main import app

runner = CliRunner()


def test_extract_cit():
    result = runner.invoke(app, ["extract", "cit", "test"])
    assert result.exit_code == 0
    assert "Extract cit test..." in result.output


def test_extract_bib():
    # write tests for extract.py
    result = runner.invoke(app, ["extract", "bib", "test"])
    assert result.exit_code == 0
    assert "Extract bib test..." in result.output
