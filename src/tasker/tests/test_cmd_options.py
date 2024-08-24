# %%
import pytest

from tasker.utils.cmd_options import CmdOptions


# %%
@pytest.mark.parametrize(
    "method, args, expected",
    [
        ("__getitem__", (0,), "--voice=Daniel"),
        ("__getitem__", (slice(1, None),), ["--sound=10", "--beaver=ten more minutes"]),
        (
            "__setitem__",
            (0, "--voice=gary"),
            ["--voice=gary", "--sound=10", "--beaver=ten more minutes"],
        ),
        ("reverse", (), ["--beaver=ten more minutes", "--sound=10", "--voice=Daniel"]),
        ("__len__", (), 3),
        ("__delitem__", (-1,), ["--voice=Daniel", "--sound=10"]),
        (
            "append",
            ("--extra=more options",),
            [
                "--voice=Daniel",
                "--sound=10",
                "--beaver=ten more minutes",
                "--extra=more options",
            ],
        ),
        (
            "extend",
            (["--another=extra option", "--one=more"],),
            [
                "--voice=Daniel",
                "--sound=10",
                "--beaver=ten more minutes",
                "--another=extra option",
                "--one=more",
            ],
        ),
    ],
)
def test_cmd_options_methods(method, args, expected):
    say_options = CmdOptions(voice="Daniel", sound=10, beaver="ten more minutes")

    result = getattr(say_options, method)(*args)
    if isinstance(result, CmdOptions):
        result = list(result)

    assert type(result) is type(expected), f"Method: {method}"
    assert result == expected, f"Method: {method}"


@pytest.mark.parametrize(
    "command, expected",
    [
        ("say_options[0]", "--voice=Daniel"),
        ("say_options[1:] #1", ["--sound=10", "--beaver=ten more minutes"]),
        ("say_options[1:] #2", ["--sound=10", "--beaver=ten more minutes"]),
        (
            "say_options.__setitem__(0, '--voice=gary')",
            [
                "--voice=gary",
                "--sound=10",
                "--beaver=ten more minutes",
            ],
        ),
        ("say_options[1]", "--sound=10"),
        (
            "say_options.reverse()",
            ["--beaver=ten more minutes", "--sound=10", "--voice=Daniel"],
        ),
        ("len(say_options)", 3),
        (
            "list(i for i in say_options)",
            ["--voice=Daniel", "--sound=10", "--beaver=ten more minutes"],
        ),
        ("say_options.__delitem__(-1)", ["--voice=Daniel", "--sound=10"]),
        (
            "say_options.append('--extra=more options')",
            [
                "--voice=Daniel",
                "--sound=10",
                "--beaver=ten more minutes",
                "--extra=more options",
            ],
        ),
        (
            "say_options.extend(['--another=extra option', '--one=more'])",
            [
                "--voice=Daniel",
                "--sound=10",
                "--beaver=ten more minutes",
                "--another=extra option",
                "--one=more",
            ],
        ),
        (
            "['--left=True'] + say_options",
            [
                "--left=True",
                "--voice=Daniel",
                "--sound=10",
                "--beaver=ten more minutes",
            ],
        ),
    ],
)
def test_cmd_options_methods2(command, expected):
    say_options = CmdOptions(voice="Daniel", sound=10, beaver="ten more minutes")  # noqa: F841

    result = eval(command)

    if isinstance(result, CmdOptions):
        result = list(result)

    assert result == expected, f"Test: {command}, \nExpected {expected}, \ngot {result}\n"


@pytest.mark.parametrize(
    "value, error",
    [
        (["--voice=Daniel", "--sound=10"], False),
        (["--voiceDaniel"], True),
        (["-sound=10"], True),
        ([10], True),
    ],
)
def test_cmd_options_validation(value, error):
    cmd_options = CmdOptions()
    if error:
        with pytest.raises(AssertionError):
            cmd_options.extend(value)
    else:
        cmd_options.extend(value)
        assert cmd_options == value
