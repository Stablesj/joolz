import re

import click

from tasker.task import data, pl_print
from tasker.utils.cli_class import CLI, add_params


def clean_name(name):
    return re.sub("_task[s]?", "", name)


class TaskCLI(CLI):
    @staticmethod
    def clean_name(name):
        return re.sub("_task[s]?", "", name)

    def todo():
        """
        Choose from the incomplete tasks.
        """
        todo = data.todo
        if len(todo) > 0:
            print("There are tasks outstanding.")
            id = data.choice(
                data.todo,
                "Input a number to continue the task, or press enter to make new task: ",
            )
            if id:
                task = data.get(id, "task")
            else:
                id = data.append()

            print("Task:", task)
        else:
            choice = input("No outstanding tasks found. Would you like to make a new task? (y/n): ")
            match choice:
                case "y":
                    id = data.append()
                case "n":
                    print("Exiting.")
                case _:
                    print("Invalid input.")

        data.start_work(id)
        data.finish_work(id)

    def delete():
        """
        Delete an item from the task list.
        """
        data.delete()

    def new_tasks():
        """
        Add an item to the task list.
        """
        data.append()

    @add_params(
        click.option("--sort", default="created", help="Sort by column."),
        click.option("--reverse", default=True, help="Reverse sort order."),
    )
    def list_tasks(sort, reverse):
        """
        Show the task list.
        """
        pl_print(data.formatted(data.df).sort(sort, descending=reverse), drop=None)

    def complete():
        """
        Mark a task as done.
        """
        data.complete()
