import os
import pathlib
from typing import Any, Callable, Optional

import dotenv


class EnvNotFoundError(FileNotFoundError):
    """Raised when no environment file can be found/loaded from any
    known locations within the system.
    """

    pass


def to_boolean(value: str) -> bool:
    """Cast a string value to a boolean.

    This function will return `True` if the value specified falls
    within one of the supported truthy values, otherwise, `False`
    is returned.
    """
    return value.lower() in ("true", "yes", "1", "on")


def to_list(value: str, separator: str = ",") -> list:
    """Cast a string value to a list.

    This function will split the value using the specified separator
    value, the resulting list is returned.
    """
    return value.split(separator)


def loadenv(base: pathlib.Path = None, name: str = ".env") -> None:
    """Attempt to load environment variables into the current system using
    the `python-dotenv` python package.

    Searches for the specified environment file `name` in a couple
    of locations, namely:

    - Provided base directory (optional).
    - Current working directory.
    - Parent of current file (utils).

    Stopping at the first environment file found that
    can be loaded.
    """
    paths = list(
        filter(
            None,
            [
                base,
                pathlib.Path.cwd(),
                pathlib.Path(__file__).resolve().parents[1],
            ],
        )
    )
    for env in (pathlib.Path(p) / name for p in paths):
        if env.is_file():
            return dotenv.load_dotenv(env)

    raise EnvNotFoundError(
        "Unable to find a valid %s file, checked: %s"
        % (
            name,
            [str(p) for p in paths],
        )
    )


def getenv(
    name: str,
    default: Optional[Any] = None,
    cast: Optional[Callable] = None,
    required: bool = False,
) -> Any:
    """Attempt to retrieve an environment variable from the current system using
    the specified `name` argument.

    An optional `default` argument can be specified to fall back to a specific value
    when the specified environment variable is unavailable.

    An optional `cast` argument can be specified to attempt to cast the environment
    variable using a callable function.

    If the `required` argument is enabled, a `ValueError` will be raised when the
    specified environment variable is unavailable.
    """
    try:
        value = os.environ[name]
    except KeyError:
        if not required:
            return default
        else:
            raise ValueError(
                "Required environment variable '%s' could not be loaded, ensure "
                "your environment file includes all required environment variables."
                % name
            )
    else:
        return cast(value) if cast else value
