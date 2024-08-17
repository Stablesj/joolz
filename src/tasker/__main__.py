# %%
import click
from tasker.countdown import countdown_cli

from tasker.task import TaskCLI, clean_name


@click.group()
def main():
    """A simple CLI for countdowns."""
    pass


main.add_command(countdown_cli, name="countdown")
for command in TaskCLI().commands:
    main.add_command(getattr(TaskCLI, command), name=clean_name(command))


if __name__ == "__main__":
    main()
