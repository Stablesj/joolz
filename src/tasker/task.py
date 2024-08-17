# %%
from loguru import logger
import subprocess
import polars as pl
from polars import col, lit
from collections import UserDict, UserList
from datetime import datetime
from pathlib import Path
from tasker.utils.cmd_options import CmdOptions
from tasker.utils.helpers import pl_print
from tasker.countdown import countdown
from tasker.utils.cli_class import MetaCLI, add_params
import click
import re

DF_FP = Path(__file__).parent / "data/tasks.csv"

df_schema = {
    "id": pl.Int64,
    "task": pl.String,
    "completed": pl.Boolean,
    "created": pl.Datetime("us"),
}


def pl_print(df, string=False, drop=("id")):
    if drop is not None:
        df = df.drop(drop)
    df = df.with_columns(col("created").dt.strftime("%Y-%m-%d %H:%M:%S"))
    with pl.Config(tbl_hide_column_data_types=True, tbl_rows=20):
        if string:
            return df.__repr__()
        print(df)


class Data:
    def __init__(self, fp=None) -> None:
        self.fp = fp or DF_FP

    @property
    def df(self):
        try:
            df = pl.read_csv(self.fp, schema=df_schema)
        except FileNotFoundError:
            df = pl.DataFrame(schema=df_schema)
        df = df.sort("created", descending=True)
        # df = df.with_row_index("id")
        assert df["id"].is_unique().all(), "Index column is not unique."
        return df

    def write(self, df: pl.DataFrame):
        assert (
            df.schema == df_schema
        ), f"Schema mismatch: \nOld: {df_schema}\nNew: {df.schema}"
        df.sort("id").write_csv(self.fp)

    def append(self, task=None):
        if task is None:
            task = input("What would you like to complete this hour?: ")
        if len(task) == 0:
            raise ValueError("Task cannot be empty.")

        df = self.df
        print(df.shape)

        # catch error if no tasks
        if (max_id := df["id"].max()) is None:
            max_id = -1
        new_id = max_id + 1

        new_row = pl.DataFrame(
            [
                [new_id],
                [task],
                [False],
                [datetime.now()],
            ],
            schema=df_schema,
        )
        df = pl.concat([df, new_row])
        self.write(df)
        return new_id

    @staticmethod
    def formatted(df):
        return (
            df.with_columns(
                done=pl.when("completed").then(lit("✅")).otherwise(lit("❌"))
            )
            .with_row_index("index")
            .drop("completed")
        )

    @property
    def todo(self):
        return self.df.filter(col("completed") == False)

    @property
    def done(self):
        return self.df.filter(col("completed") == True)

    def delete(self, id=None):
        df = self.df
        id = id if id is not None else self.choice(df, "Input task number to delete: ")
        assert isinstance(id, int), f"Invalid task id, need int, got {type(id)}."
        match id:
            case int():
                assert id in df["id"], f"Task {id=} does not exist."
                deleted = df.filter(col("id") == id).row(0, named=True)
                df = df.filter(col("id") != id)
                self.write(df)
                print(f"""Deleted task {id=}: "{deleted['task']}".""")
            case _:
                print("No task deleted.")

    def choice(self, df, prompt):
        if len(df) == 0:
            raise ValueError("No tasks found.")
        assert "id" in df.columns, "Index column not found."
        df = self.formatted(df)
        pl_print(df)
        choice = input(prompt)
        match choice:
            case str() if choice.isdigit():
                choice = int(choice)
                # print("Integer choice")
                assert choice in df["index"], f"Task {choice} does not exist."
                return df.row(choice, named=True)["id"]
            case _:
                # print("Not integer choice")
                return None

    def _set(self, id, column, value):
        df = self.df
        df = df.with_columns(
            pl.when(col("id") == id)
            .then(lit(value))
            .otherwise(col(column))
            .alias(column)
        )
        self.write(df)

    def get_row(self, id: int) -> dict:
        return self.df.filter(col("id") == id).row(0, named=True)

    def get(self, id, column):
        return self.df.filter(col("id") == id)[column].item()

    def complete(self, id=None, completed=True):
        if id is None:
            id = self.choice(self.todo, "Input task number to complete: ")
        self._set(id, "completed", completed)

    def __repr__(self):
        return pl_print(self.formatted(self.df), string=True, drop=None)


def sound_alert():
    say_options = CmdOptions(
        # Alex, Daniel, Fiona, Fred, Samantha or Victoria
        voice="Daniel",
    )

    subprocess.run(["say"] + say_options + ["Hours up!"])


data = Data()


def start_work(id):
    task = data.get(id, "task")
    countdown("1s", title=task)


def finish_work(id):
    complete = input("Task complete? (y/n): ")

    match complete:
        case "y":
            data.complete(id)
        case "n":
            print("Task not completed.")
        case _:
            print("Invalid input.")


def clean_name(name):
    return re.sub("_task[s]?", "", name)


class TaskCLI(metaclass=MetaCLI):
    def __init__(self) -> None:
        # Create the Click group
        self.cli = click.Group()

        # Register commands
        for command in self.commands:
            self.cli.add_command(getattr(self, command), name=self.clean_name(command))

    @staticmethod
    def clean_name(name):
        return re.sub("_task[s]?", "", name)

    def run(self):
        # Run the cli
        self.cli()

    def todo():
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
            choice = input(
                "No outstanding tasks found. Would you like to make a new task? (y/n): "
            )
            match choice:
                case "y":
                    id = data.append()
                case "n":
                    print("Exiting.")
                case _:
                    print("Invalid input.")

        start_work(id)
        finish_work(id)

    def delete():
        data.delete()

    def new_tasks():
        data.append()

    @add_params(
        click.option("--sort", default="created", help="Sort by column."),
        click.option("--reverse", default=True, help="Reverse sort order."),
    )
    def list_tasks(sort, reverse):
        pl_print(data.formatted(data.df).sort(sort, descending=reverse), drop=None)

    def complete():
        data.complete()


if __name__ == "__main__":
    cli = TaskCLI()
    cli.run()
