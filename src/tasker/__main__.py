# %%
import click

from tasker.commands.task_cli import TaskCLI, clean_name
from tasker.countdown import countdown_cli


@click.group()
def main():
    """A simple CLI for countdowns."""
    pass


main.add_command(countdown_cli, name="countdown")
for command in TaskCLI().commands:
    main.add_command(getattr(TaskCLI, command), name=clean_name(command))


if __name__ == "__main__":
    main()
