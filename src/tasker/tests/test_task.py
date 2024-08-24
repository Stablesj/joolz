# %%
from pathlib import Path

import pytest

from tasker import task

cwd = Path(__file__).resolve().parent


@pytest.fixture
def data(fname="tasks.csv"):
    return task.Data(fp=cwd / f"data/{fname}")


@pytest.fixture
def data_write(fname="tasks_write.csv"):
    return task.Data(fp=cwd / f"data/{fname}")


# write tests for the Data class
def test_data_df(data):
    assert data.df.shape[1] == 4
    assert data.df.schema == task.df_schema
    assert data.df["id"].is_unique().all()


def test_data_write(data_write):
    df = data_write.df
    data_write.write(df)
    assert (data_write.fp).exists()
    Path(data_write.fp).unlink()  # cleanup


def test_data_append(data_write):
    Path(data_write.fp).unlink(missing_ok=True)
    _ = data_write.df  # initialise dataframe
    _ = data_write.append("test task")
    assert data_write.df.shape == (1, 4)
    assert data_write.df["task"][0] == "test task"
    assert data_write.df["completed"][0] == False  # noqa: E712
    assert data_write.df["created"][0] == data_write.df["created"].max()
    Path(data_write.fp).unlink()  # cleanup


def test_data_formatted(data):
    df = data.df
    formatted = data.formatted(df)
    # check for columns
    assert "task" in formatted.columns
    assert "created" in formatted.columns
    # added columns
    assert "index" in formatted.columns
    assert "done" in formatted.columns
    # removed columns
    assert "id" in formatted.columns
    assert "completed" not in formatted.columns


def test_data_append_empty(data_write):
    Path(data_write.fp).unlink(missing_ok=True)
    with pytest.raises(ValueError):
        _ = data_write.append("")
    assert data_write.df.shape == (0, 4)
    assert not Path(data_write.fp).exists()


def test_data_delete(data_write):
    Path(data_write.fp).unlink(missing_ok=True)
    _ = data_write.append("test task")
    _ = data_write.append("test task 2")
    assert data_write.df.shape == (2, 4)
    _ = data_write.delete(0)
    assert data_write.df.shape == (1, 4)
    assert data_write.df["task"][0] == "test task 2"
    Path(data_write.fp).unlink(missing_ok=False)  # cleanup


def test_data_complete(data_write):
    Path(data_write.fp).unlink(missing_ok=True)
    _ = data_write.append("test task")
    _ = data_write.append("test task 2")
    assert data_write.df.shape == (2, 4)
    _ = data_write.complete(0)
    assert data_write.df.shape == (2, 4)
    assert data_write.get(0, "completed") == True  # noqa: E712
    Path(data_write.fp).unlink(missing_ok=False)  # cleanup


def test_data_get(data_write):
    Path(data_write.fp).unlink(missing_ok=True)
    data_write.append("test task")
    data_write.append("test task 2")
    assert data_write.get(0, "task") == "test task"
    assert data_write.get(1, "task") == "test task 2"
    Path(data_write.fp).unlink(missing_ok=False)  # cleanup


def test_data_set(data_write):
    Path(data_write.fp).unlink(missing_ok=True)
    data_write.append("test task")
    data_write.append("test task 2")
    data_write._set(0, "task", "new task")
    assert data_write.get(0, "task") == "new task"
    Path(data_write.fp).unlink(missing_ok=False)  # cleanup


# %%
