"""Command-line interface."""

# %%
import re
import shutil
import sys
import time

import click

ENABLE_ALT_BUFFER = "\033[?1049h"
DISABLE_ALT_BUFFER = "\033[?1049l"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

DURATION_RE = re.compile(
    r"""
    ^
    (?:                 # Optional minutes
        ( \d{1,2} )     # D or DD
        m               # "m"
    )?
    (?:                 # Optional seconds
        ( \d{1,2} )     # D or DD
        s               # "s"
    )?
    $
""",
    re.VERBOSE,
)

CHARS = {
    "0": "██████\n██  ██\n██  ██\n██  ██\n██████",
    "1": "   ██ \n  ███ \n   ██ \n   ██ \n   ██ ",
    "2": "██████\n    ██\n██████\n██    \n██████",
    "3": "██████\n    ██\n █████\n    ██\n██████",
    "4": "██  ██\n██  ██\n██████\n    ██\n    ██",
    "5": "██████\n██    \n██████\n    ██\n██████",
    "6": "██████\n██    \n██████\n██  ██\n██████",
    "7": "██████\n    ██\n   ██ \n  ██  \n  ██  ",
    "8": " ████ \n██  ██\n ████ \n██  ██\n ████ ",
    "9": "██████\n██  ██\n██████\n    ██\n █████",
    ":": "  \n██\n  \n██\n  ",
}
CLEAR = "\033[H\033[J"


def str_to_duration(string):
    """Convert given XmXs string to seconds (as an integer)."""
    match = DURATION_RE.search(string)
    if not match:
        raise ValueError(f"Invalid duration: {string}")
    minutes, seconds = match.groups()
    return int(minutes or 0) * 60 + int(seconds or 0)


def countdown(duration: int, title: str = None):
    """Core countdown logic, separated from CLI interface."""
    if isinstance(duration, str):
        duration = str_to_duration(duration)

    enable_ansi_escape_codes()
    print(ENABLE_ALT_BUFFER + HIDE_CURSOR, end="")
    try:
        for n in range(duration, -1, -1):
            lines = get_number_lines(n)
            print_full_screen(lines, title)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print(SHOW_CURSOR + DISABLE_ALT_BUFFER, end="")


@click.command()
@click.version_option(package_name="countdown-cli")
@click.argument("duration", type=str_to_duration)
@click.option("--title", type=str, default=None, help="Title for the countdown clock.")
def countdown_cli(duration, title):
    """Countdown from the given duration to 0.

    DURATION should be a number followed by m or s for minutes or seconds.

    Examples of DURATION:

    \b
    - 5m (5 minutes)
    - 45s (45 seconds)
    - 2m30s (2 minutes and 30 seconds)
    """  # noqa: D301
    countdown(duration, title)


def enable_ansi_escape_codes():
    """If running on Windows, enable ANSI escape codes."""
    if sys.platform == "win32":  # pragma: no cover
        from ctypes import windll

        k = windll.kernel32
        stdout = -11
        enable_processed_output = 0x0001
        enable_wrap_at_eol_output = 0x0002
        enable_virtual_terminal_processing = 0x0004
        k.SetConsoleMode(
            k.GetStdHandle(stdout),
            enable_processed_output
            | enable_wrap_at_eol_output
            | enable_virtual_terminal_processing,
        )


def print_full_screen(lines, title=None):
    """Print the given lines centered in the middle of the terminal window."""
    width, height = shutil.get_terminal_size()
    max_length = max(len(line) for line in lines)
    width -= max_length
    # insert title above the countdown
    title_hspace = 2
    lines = add_title_lines(lines, title or "", hspace=title_hspace)
    height -= len(lines) + 2
    # subtract the hspace from the vertical_pad to center the countdown clock
    vertical_pad = "\n" * ((height - title_hspace) // 2)
    padded_text = "\n".join(" " * (width // 2) + line for line in lines)
    print(CLEAR + vertical_pad + padded_text, flush=True)


def add_title_lines(lines, title, hspace):
    """Add title to the top of the lines."""
    max_length = max(len(line) for line in lines)
    title_line = f" {title} ".center(max_length)
    return [title_line] + [""] * hspace + lines


def get_number_lines(seconds):
    """Return list of lines which make large MM:SS glyphs for given seconds."""
    lines = [""] * 5
    minutes, seconds = divmod(seconds, 60)
    time = f"{minutes:02d}:{seconds:02d}"
    for char in time:
        char_lines = CHARS[char].splitlines()
        for i, line in enumerate(char_lines):
            lines[i] += line + " "
    # lines = ["Task title"] + [""] * 3 + lines
    return lines


if __name__ == "__main__":
    countdown_cli(prog_name="countdown")  # pragma: no cover

# %%
