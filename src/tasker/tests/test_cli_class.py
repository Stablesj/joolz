import click
import pytest
from click.testing import CliRunner

from tasker.utils.cli_class import CLI, add_params


class FixtureCLI(CLI):
    @staticmethod
    def clean_name(x):
        return x.removesuffix("_bacon")

    def add():
        print("running add command")

    @add_params(click.option("--param1", default="new", type=int, help="parameter help"))
    def new(param1):
        """
        New method added
        """
        print(f"command with params: {param1}")

    def pancakes_bacon():
        """
        Help me I love bacon.
        """
        print("bacon method")


@pytest.fixture
def cli_runner():
    return CliRunner()


def test_add_command(cli_runner):
    result = cli_runner.invoke(FixtureCLI().cli, ["add"])
    assert result.exit_code == 0
    assert "running add command" in result.output


def test_new_command(cli_runner):
    result = cli_runner.invoke(FixtureCLI().cli, ["new", "--param1", "10"])
    assert result.exit_code == 0
    assert "command with params: 10" in result.output, f"got {result.output}"


def test_pancakes_bacon_command(cli_runner):
    result = cli_runner.invoke(FixtureCLI().cli, ["pancakes"])
    assert result.exit_code == 0, f"{result.exit_code=}"
    assert "bacon method" in result.output


def test_help(cli_runner):
    result = cli_runner.invoke(FixtureCLI().cli, ["--help"])
    assert result.exit_code == 0
    assert "add" in result.output
    assert "new" in result.output
    assert "pancakes" in result.output
    assert "Help me I love bacon." in result.output


if __name__ == "__main__":
    FixtureCLI().run()
