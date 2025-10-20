import inspect
from os import PathLike
import importlib.util
import sys
from types import ModuleType


def load(name: str, path: str | PathLike[str]):
    """
    Loads and executes a module from the file system based on its
    path.

    If no module is found a `FileNotFoundError` is raised, else,
    it is registered in the `sys.modules` `dict` with the given
    `name`.

    This function returns the loaded module, which can be stored
    in a global variable to be accessible like a staticly imported
    module.
    """

    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise FileNotFoundError(
            f"Could not load module '{name}' from path '{path}'")

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    sys.modules[name] = module

    return module


def get_classes(module: ModuleType):
    """
    Returns a `list` with `tuples` storing the name and value of
    the classes of a given `module`.
    """

    return list(filter(
        lambda member_data: member_data[1].__module__ == module.__name__,
        inspect.getmembers(module, inspect.isclass)
    ))


def get_functions(module: ModuleType):
    """
    Returns a `list` with `tuples` storing the name and value of
    the functions of a given `module`.
    """

    return list(filter(
        lambda function_data: function_data[1].__module__ == module.__name__,
        inspect.getmembers(module, inspect.isfunction)
    ))
