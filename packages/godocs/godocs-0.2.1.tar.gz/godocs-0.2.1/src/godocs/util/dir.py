from os import PathLike
from pathlib import Path
from typing import Callable


def get_subitems(
    path: str | PathLike[str],
    exclude: list[str] | None = None,
    include: list[str] | None = None,
    predicate: Callable[[Path], bool] | None = None,
) -> list[Path]:
    """
    Returns a `list` with the `Paths` of the subitems
    (both files and or directories) of the `path` passed,
    excluding the ones from the `exclude` list and
    including only the ones from the `include` list (if any).
    """

    if exclude is None:
        exclude = []
    if include is None:
        include = []
    if predicate is None:
        predicate = (lambda _: True)

    path = Path(path)

    subitems: list[Path] = []

    for p in path.iterdir():
        if p.name in exclude:
            continue
        if len(include) > 0 and not p.name in include:
            continue
        if not predicate(p):
            continue

        subitems.append(p)

    return subitems


def get_subdirs(
    path: str | PathLike[str],
    exclude: list[str] | None = None,
    include: list[str] | None = None,
    predicate: Callable[[Path], bool] | None = None,
) -> list[Path]:
    """
    Returns a `list` with the `Paths` of the subdirectories of
    the `path` passed, excluding the ones from the `exclude`
    list and including only the ones from the `include` list
    (if any).
    """

    return get_subitems(
        path,
        exclude,
        include,
        predicate=lambda p: p.is_dir() and (
            predicate(p) if predicate is not None else True)
    )
