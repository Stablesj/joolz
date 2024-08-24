# %%
from abc import abstractmethod
from functools import wraps

import click
from loguru import logger


def error_catch(func):
    """Catch errors and print them to the console.
    Useful for running in the cli.

    Parameters
    ----------
    func : callable
        The function to wrap.
    """

    @wraps(func)  # needed so metadata is passed to click.command
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")

    return wrapper


from functools import wraps


def add_params(*options):
    """Add metadata to a function."""

    def decorator(func):
        """Decorator to add metadata to a function.

        Parameters
        ----------
        func : callable
            The function to add metadata to.

        Returns
        -------
        callable
            The wrapped function with metadata.
        """
        # Update the _params attribute with the provided metadata
        func._params = options  # _params are not exposed to the metadata as the function is then wrapped
        # print(f"Adding metadata: {len(options)=} to {func.__name__}")
        
        @wraps(func)  # Preserve function metadata
        def wrapped(*args, **kwargs):
            # print(f"Calling {func.__name__} with metadata: {func._params}")
            return func(*args, **kwargs)

        # preserves metadata like @wraps does
        # Transfer existing _params if present, or set new one
        # assert not hasattr(
        #     func, "_params"
        # ), f"Function {func.__name__} already has _params."
        # wrapped._params = options

        # Preserve other function attributes if necessary
        # wrapped.__name__ = func.__name__
        # wrapped.__doc__ = func.__doc__

        return wrapped

    return decorator


class MetaCLI(type):
    # List of methods that should not be added as commands
    not_commands = ["__init__", "cli", "run", "clean_name"]

    def __new__(cls, name, bases, dct):
        # have to initialise it in __new__ to avoid sharing between instances of the class
        commands = []

        for key, value in dct.items():
            # Loop through the methods in the class and add them as commands
            if callable(value) and key not in cls.not_commands:
                commands.append(key)

                # Check if the function has parameters before wrapping it
                params = getattr(value, "_params", None)

                value = staticmethod(value)

                # errors if trying to get _params here, after wrapping

                if not dct.get("debug"):
                    value = error_catch(value)

                # check if the function has params to add
                if params:
                    # Wrap the function with the parameter wrappers.
                    for option in params:
                        value = option(value)
                    logger.debug(f"Added options {[opt.opts[0] for opt in value.__click_params__]} to {key}")
                else:
                    logger.debug(f"No params found for {key}")

                dct[key] = click.command(value)

        dct["commands"] = commands
        return super().__new__(cls, name, bases, dct)


class CLI(metaclass=MetaCLI):
    """CLI class for subclassing.

    Attributes
    __________
    cli: click.Group
        main cli call point for the group.
    commands: list
        list of all the commands to run

    Methods
    -------
    run
        calls the cli

    clean_name
        abstractmethod.
        function to clean the command names for the cli.
    """

    def __init__(self) -> None:
        # Create the Click group
        self.cli = click.Group()

        # Register commands
        for command in self.commands:
            self.cli.add_command(getattr(self, command), name=self.clean_name(command))

    def run(self):
        # Run the cli
        self.cli()

    @abstractmethod
    def clean_name(self, command):
        pass
