# %%
import click
import loguru


def error_catch(func):
    """Catch errors and print them to the console.
    Useful for running in the cli.

    Parameters
    ----------
    func : callable
        The function to wrap.
    """

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")

    return wrapper


from functools import wraps


def add_params(*meta_data):
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
        func._params = meta_data  # _params are not exposed to the metadata as the function is then wrapped
        # print(f"Adding metadata: {len(meta_data)=} to {func.__name__}")

        @wraps(func)  # Preserve function metadata
        def wrapped(*args, **kwargs):
            # print(f"Calling {func.__name__} with metadata: {func._params}")
            return func(*args, **kwargs)

        # preserves metadata like @wraps does
        # Transfer existing _params if present, or set new one
        # assert not hasattr(
        #     func, "_params"
        # ), f"Function {func.__name__} already has _params."
        # wrapped._params = meta_data

        # Preserve other function attributes if necessary
        # wrapped.__name__ = func.__name__
        # wrapped.__doc__ = func.__doc__

        return wrapped

    return decorator


class MetaCLI(type):
    commands = []
    # List of methods that should not be added as commands
    not_commands = ["__init__", "cli", "run", "clean_name"]

    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            # Loop through the methods in the class and add them as commands
            if callable(value) and key not in cls.not_commands:
                cls.commands.append(key)

                # Check if the function has parameters before wrapping it
                # if hasattr(value, "_params"):
                #     params = value._params
                # else:
                #     params = None

                params = getattr(value, "_params", None)

                value = staticmethod(value)

                # errors if trying to get _params here, after wrapping

                value = error_catch(value)

                # check if the function has params to add
                if params:
                    # Wrap the function with the parameter wrappers.
                    for option in params:
                        print(f"Adding option: {option} to {key}")
                        value = option(value)
                else:
                    print(f"No params found for {key}")

                dct[key] = click.command(value)

        dct["commands"] = cls.commands
        return super().__new__(cls, name, bases, dct)
