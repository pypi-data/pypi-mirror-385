"""Functions related to files and folders."""

import logging
import time
from collections.abc import Generator
from fnmatch import fnmatch
from pathlib import Path
from typing import IO, Any, NamedTuple

from pyauxlib.decorators import deprecated_argument
from pyauxlib.fileutils.utils import clean_file_extension

logger = logging.getLogger(__name__)


class FileRelPath(NamedTuple):
    """Represents a file's absolute and relative paths.

    Attributes
    ----------
    file : Path
        Absolute path.
    rel_path : Path
        Path relative to parent directory.
    """

    file: Path
    rel_path: Path


def iterate_files(
    pathobject: Path, file_extensions: list[str] | None = None
) -> Generator[FileRelPath, None, None]:
    """Yield files in a path with optional extension filtering.

    For directories, searches only the immediate contents without recursing into subdirectories.
    For files, simply returns the file itself regardless of extension filtering.

    Parameters
    ----------
    pathobject : Path
        The Path object to search for files. Can be either a file or directory path.
    file_extensions : list[str], optional
        If provided, only files with these extensions will be included in the results.
        Extensions are case-insensitive. When pathobject is a file, this parameter is ignored.

    Returns
    -------
    Generator[FileRelPath, None, None]
        A stream of FileRelPath objects, each containing both the absolute path to the file
        and its path relative to the 'pathobject'

    Raises
    ------
    FileNotFoundError
        When the specified 'pathobject' does not exist in the filesystem
    """
    if not pathobject.exists():
        error_msg = f"File or folder '{pathobject}' does not exist."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    if pathobject.is_file():
        yield FileRelPath(pathobject, Path())

    if pathobject.is_dir():
        yield from iterate_folder(
            folder=pathobject,
            file_extensions=file_extensions,
            subfolders=False,
            parent_path=pathobject,
        )


def _iterate_folder_internal(  # noqa: PLR0913
    folder: str | Path,
    file_extensions: list[str] | None = None,
    include_patterns: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    subfolders: bool = True,
    parent_path: Path | None = None,
) -> Generator[FileRelPath, None, None]:
    """Yield files from a a folder with flexible filtering options for extensions and patterns.

    Supports both extension-based and pattern-based filtering, with options to include or exclude
    files matching the specified patterns. Can search recursively through subdirectories if desired.

    Parameters
    ----------
    folder : str | Path
        The starting folder path for the file search. If a file path is provided, searches its
        parent directory
    file_extensions : list[str], optional
        If provided, only files with these extensions will be included. Extensions are
        case-insensitive.
    include_patterns : list[str], optional
        Glob patterns for filtering files by name. Files matching any pattern are included.
        Patterns can include wildcards like '*' and '?', to match multiple characters or a single
        character, respectively.
        Pattern examples:
        - ["*before*"]: Files containing 'before' anywhere in the name.
        - ["*.txt"]: Files with the '.txt' extension.
        - ["file_?.txt"]: Files with names like 'file_1.txt', 'file_2.txt', etc.
        - ["file_[0-9].txt"]: Equivalent to the previous example, but uses a character set to match
        any single digit between 0 and 9.
    exclude_patterns : list[str], optional
        Glob patterns for filter files by name to be excluded.
    subfolders : bool, optional
        When True, performs a recursive search through all subdirectories. Otherwise, only
        searches the immediate folder contents.
    parent_path : Path, optional
        Reference path used for calculating relative paths in the results. If None, uses the
        search starting folder.

    Returns
    -------
    Generator[FileRelPath, None, None]
        A stream of FileRelPath objects, each containing both the absolute path to a matched
        file and its path relative to parent_path

    Raises
    ------
    FileNotFoundError
        When the specified folder path does not exist in the filesystem.
    """
    current_folder = Path(folder).parent if Path(folder).is_file() else Path(folder)

    if not current_folder.exists():
        msg = f"The folder '{current_folder}' does not exist."
        raise FileNotFoundError(msg)

    file_extensions = (
        [clean_file_extension(ext) for ext in file_extensions] if file_extensions else None
    )
    parent_path = parent_path or current_folder

    files = current_folder.rglob("*") if subfolders else current_folder.glob("*")
    for file in files:
        if not file.is_file():
            continue

        # Check extensions
        if file_extensions and file.suffix.lower() not in file_extensions:
            continue

        # Check patterns
        if include_patterns and not any(fnmatch(file.name, pat) for pat in include_patterns):
            continue
        if exclude_patterns and any(fnmatch(file.name, pat) for pat in exclude_patterns):
            continue

        yield FileRelPath(file=file, rel_path=file.relative_to(parent_path))


@deprecated_argument(
    ["file_patterns"],
    since="v0.13",
    additional_msg="Use the new API with 'include_patterns' and 'exclude_patterns'",
)
def iterate_folder(  # noqa: PLR0913
    folder: str | Path,
    file_extensions: list[str] | None = None,
    file_patterns: list[str] | None = None,  # DEPRECATED
    include_patterns: list[str] | None = None,
    exclude_patterns: bool | list[str] | None = None,
    subfolders: bool = True,
    parent_path: Path | None = None,
) -> Generator[FileRelPath, None, None]:
    """Yield files from a a folder with flexible filtering options for extensions and patterns.

    Supports both extension-based and pattern-based filtering, with options to include or exclude
    files matching the specified patterns. Can search recursively through subdirectories if desired.

    Parameters
    ----------
    folder : str | Path
        The starting folder path for the file search. If a file path is provided, searches its
        parent directory
    file_extensions : list[str], optional
        If provided, only files with these extensions will be included. Extensions are
        case-insensitive.
    file_patterns : list[str], optional # DEPRECATED
        Glob patterns for filtering files by name. Files matching any pattern are included.
        Patterns can include wildcards like '*' and '?', to match multiple characters or a single
        character, respectively.
        Pattern examples:
        - ["*before*"]: Files containing 'before' anywhere in the name.
        - ["*.txt"]: Files with the '.txt' extension.
        - ["file_?.txt"]: Files with names like 'file_1.txt', 'file_2.txt', etc.
        - ["file_[0-9].txt"]: Equivalent to the previous example, but uses a character set to match
        any single digit between 0 and 9.
    include_patterns : list[str], optional
        Glob patterns for filtering files by name. Files matching any pattern are included.
        Patterns can include wildcards like '*' and '?', to match multiple characters or a single
        character, respectively.
        Pattern examples:
        - ["*before*"]: Files containing 'before' anywhere in the name.
        - ["*.txt"]: Files with the '.txt' extension.
        - ["file_?.txt"]: Files with names like 'file_1.txt', 'file_2.txt', etc.
        - ["file_[0-9].txt"]: Equivalent to the previous example, but uses a character set to match
        any single digit between 0 and 9.
    exclude_patterns : bool | list[str], optional
        Glob patterns for filter files by name to be excluded.
        'True' is used by file_patterns, to reverse the inclusion to an exclusion. Use of bool
        is # DEPRECATED.
    subfolders : bool, optional
        When True, performs a recursive search through all subdirectories. Otherwise, only
        searches the immediate folder contents.
    parent_path : Path, optional
        Reference path used for calculating relative paths in the results. If None, uses the
        search starting folder.

    Returns
    -------
    Generator[FileRelPath, None, None]
        A stream of FileRelPath objects, each containing both the absolute path to a matched
        file and its path relative to parent_path

    Raises
    ------
    FileNotFoundError
        When the specified folder path does not exist in the filesystem.
    """
    # Resolve deprecated args
    include_patterns_resolved = include_patterns
    exclude_patterns_resolved = exclude_patterns if isinstance(exclude_patterns, list) else None

    # Convert deprecated args if used
    if file_patterns is not None:
        if exclude_patterns is True:
            exclude_patterns_resolved = file_patterns
            include_patterns_resolved = None
        else:
            include_patterns_resolved = file_patterns
            exclude_patterns_resolved = None

    return _iterate_folder_internal(
        folder=folder,
        file_extensions=file_extensions,
        include_patterns=include_patterns_resolved,
        exclude_patterns=exclude_patterns_resolved,
        subfolders=subfolders,
        parent_path=parent_path,
    )


def open_file(path: Path, mode: str = "w", encoding: str | None = None) -> IO[Any]:
    """Safely open a file using the provided path, mode, and encoding.

    This function ensures that the folder containing the file exists before attempting to open it.

    Parameters
    ----------
    path : Path
        The path to the file to be opened.
    mode : str, optional
        The mode in which the file is to be opened, by default 'w'.
    encoding : str | None, optional
        The encoding to be used when opening the file, by default None.

    Returns
    -------
    IO[Any]
        The opened file.

    Raises
    ------
    PermissionError
        If the function does not have permission to create the directory or open the file.
    """
    try:
        return path.open(mode=mode, encoding=encoding)
    except FileNotFoundError:
        if mode in {"r", "r+"}:
            # If trying to read but the file doesn't exist, re-raise the exception
            raise

        folder_created = create_folder(path, True)
        try:
            return path.open(mode=mode, encoding=encoding)
        except Exception:
            if folder_created and not any(path.iterdir()):
                path.rmdir()
            raise


def create_folder(path: Path, includes_file: bool = False) -> bool:
    """Create the folder passed in the 'path' if it doesn't exist.

    Useful to be sure that a folder exists before saving a file.

    Parameters
    ----------
    path : Path
        Path object for the folder (can also include the file)
    includes_file : bool, optional
        The path includes a file at the end, by default 'False'.

    Returns
    -------
    bool
        True if the folder was created, False otherwise.
    """
    path = path.parent if includes_file else path

    if path.exists():
        return False

    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        logger.warning("Failed to create folder '%s': no permission", path)
        raise
    else:
        return True


def clean_filename(filename: str, replacement: str = "_") -> str:
    """Remove illegal characters from a filename.

    Parameters
    ----------
    filename : str
        name of the file

    replacement : str
        character to replace the illegal characters

    Returns
    -------
    str
        clean name
    """
    illegal_characters = "!@#$%^&*()[]{};:,/<>?'\\'|`~-=_+"

    replacement = "_" if replacement in illegal_characters else replacement

    filename = filename.translate({ord(c): replacement for c in illegal_characters})
    return filename


def generate_unique_filename(file: Path | str, width: int = 3) -> Path:
    """Generate a unique filename by appending a zero-padded counter if needed.

    Parameters
    ----------
    file : Union[str, Path]
        The original file path.
    width : int
        The number of digits to pad the counter with (default is 3).

    Returns
    -------
    Path
        The unique file path.

    Examples
    --------
    >>> print(get_unique_filename("/path/to/file.txt"))  # doctest: +SKIP
    /path/to/file_001.txt
    """
    counter = 1
    file = Path(file)
    file_path = file

    while file_path.exists():
        new_filename = f"{file.stem}_{counter:0{width}d}{file.suffix}"
        file_path = file.parent / new_filename
        counter += 1

    return file_path


def add_folder_timestamp(rootdir: str | Path, fmt: str = "run_%Y_%m_%d-%H_%M_%S") -> Path:
    """Create a new folder with a timestamp in the given directory.

    This function takes a directory path and creates a new folder within that directory.
    The name of the new folder is a timestamp formatted according to the provided format string.

    Parameters
    ----------
    rootdir : str | Path
        The path of the directory where the new folder will be created.
    fmt : str, optional
        The format of the timestamp to be used as the new folder's name.
        The format is defined using strftime directives. Default is "run_%Y_%m_%d-%H_%M_%S".

    Returns
    -------
    Path
        The path of the newly created folder.

    Examples
    --------
    ```python
    new_folder_path = add_folder_timestamp("/path/to/directory", "run_%Y_%m_%d-%H_%M_%S")
    print(new_folder_path)
    # Output: /path/to/directory/run_2023_04_05-16_25_03
    ```
    """
    run_id = time.strftime(fmt)
    return Path(rootdir, run_id)


def ensure_file_exists(file: Path | str) -> Path:
    """Ensure that a file exists and is not a directory.

    Parameters
    ----------
    file : Path | str
        Path to the file to validate.

    Returns
    -------
    Path
        The resolved Path object of the existing file.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    IsADirectoryError
        If the specified path is a directory, not a file.
    """
    file = Path(file).resolve()

    if file.is_dir():
        msg = f"Expected a file, but got a directory: {file}"
        raise IsADirectoryError(msg)
    if not file.exists():
        msg = f"File not found: {file}"
        raise FileNotFoundError(msg)

    return file
