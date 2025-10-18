from __future__ import annotations

import ctypes
import sys
from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
from os import F_OK, R_OK, W_OK, X_OK, access, getenv, path
from pathlib import Path
from typing import IO, Any, BinaryIO, Callable, Literal, overload

from ..exceptions import FileIsADirectoryError, FileNotExistsError, FilePermissionError, FileWasNotFoundError
from ..types import (
    FileOpener,
    FilePathType,
    FuncExcept,
    OpenBinaryMode,
    OpenBinaryModeReading,
    OpenBinaryModeUpdating,
    OpenBinaryModeWriting,
    OpenTextMode,
    SPath,
)

__all__ = [
    "add_script_path_hook",
    "check_perms",
    "get_script_path",
    "get_user_data_dir",
    "open_file",
    "remove_script_path_hook",
]

_script_path_hooks = list[Callable[[], SPath | None]]()


def add_script_path_hook(hook: Callable[[], SPath | None]) -> None:
    _script_path_hooks.append(hook)


def remove_script_path_hook(hook: Callable[[], SPath | None]) -> None:
    _script_path_hooks.remove(hook)


def get_script_path() -> SPath:
    for hook in reversed(_script_path_hooks):
        if (script_path := hook()) is not None:
            return script_path

    import __main__

    try:
        path = SPath(__main__.__file__)
        return path if path.exists() else SPath.cwd()
    except AttributeError:
        return SPath.cwd()


def get_user_data_dir() -> Path:
    """Get user data dir path."""

    if sys.platform == "win32":
        buf = ctypes.create_unicode_buffer(1024)
        ctypes.windll.shell32.SHGetFolderPathW(None, 28, None, 0, buf)

        if any(ord(c) > 255 for c in buf):
            buf2 = ctypes.create_unicode_buffer(1024)
            if ctypes.windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
                buf = buf2

        return Path(path.normpath(buf.value))
    elif sys.platform == "darwin":
        return Path(path.expanduser("~/Library/Application Support/"))
    else:
        return Path(getenv("XDG_DATA_HOME", path.expanduser("~/.local/share")))


def check_perms(
    file: FilePathType, mode: OpenTextMode | OpenBinaryMode, strict: bool = False, *, func: FuncExcept | None = None
) -> bool:
    """
    Confirm whether the user has write/read access to a file.

    :param file:                    Path to file.
    :param mode:                    Read/Write mode.
    :param func:                    Function that this was called from, only useful to *func writers.

    :param:                         True if the user has write/read access, else False.

    :raises FileNotExistsError:     File could not be found.
    :raises FilePermissionError:    User does not have access to the file.
    :raises FileIsADirectoryError:  Given path is a directory, not a file.
    :raises FileWasNotFoundError:   Parent directories exist, but the given file could not be found.
    """

    file = Path(str(file))
    got_perms = False

    mode_i = F_OK

    if func is not None and not str(file):
        raise FileNotExistsError(file, func)

    for char in "rbU":
        mode_str = mode.replace(char, "")

    if not mode_str:  # pyright: ignore[reportPossiblyUnboundVariable]
        mode_i = R_OK
    elif "x" in mode_str:
        mode_i = X_OK
    elif "+" in mode_str or "w" in mode_str:
        mode_i = W_OK

    check_file = file

    if not strict and mode_i != R_OK:
        while not check_file.exists():
            check_file = check_file.parent

    if strict and file.is_dir():
        raise FileIsADirectoryError(file, func)

    got_perms = access(check_file, mode_i)

    if func is not None and not got_perms:
        if strict and not file.exists():
            if file.parent.exists():
                raise FileWasNotFoundError(file, func)

            raise FileNotExistsError(file, func)

        raise FilePermissionError(file, func)

    return got_perms


@overload
def open_file(
    file: FilePathType,
    mode: OpenTextMode = "r",
    buffering: int = ...,
    encoding: str | None = None,
    errors: str | None = ...,
    newline: str | None = ...,
    *,
    func: FuncExcept | None = None,
) -> TextIOWrapper: ...


@overload
def open_file(
    file: FilePathType,
    mode: OpenBinaryMode,
    buffering: Literal[0],
    encoding: None = None,
    *,
    func: FuncExcept | None = None,
) -> FileIO: ...


@overload
def open_file(
    file: FilePathType,
    mode: OpenBinaryModeUpdating,
    buffering: Literal[-1, 1] = ...,
    encoding: None = None,
    *,
    func: FuncExcept | None = None,
) -> BufferedRandom: ...


@overload
def open_file(
    file: FilePathType,
    mode: OpenBinaryModeWriting,
    buffering: Literal[-1, 1] = ...,
    encoding: None = None,
    *,
    func: FuncExcept | None = None,
) -> BufferedWriter: ...


@overload
def open_file(
    file: FilePathType,
    mode: OpenBinaryModeReading,
    buffering: Literal[-1, 1] = ...,
    encoding: None = None,
    *,
    func: FuncExcept | None = None,
) -> BufferedReader: ...


@overload
def open_file(
    file: FilePathType,
    mode: OpenBinaryMode,
    buffering: int = ...,
    encoding: None = None,
    *,
    func: FuncExcept | None = None,
) -> BinaryIO: ...


@overload
def open_file(
    file: FilePathType,
    mode: str,
    buffering: int = ...,
    encoding: str | None = ...,
    errors: str | None = ...,
    newline: str | None = ...,
    closefd: bool = ...,
    opener: FileOpener | None = ...,
    *,
    func: FuncExcept | None = None,
) -> IO[Any]: ...


def open_file(file: FilePathType, mode: Any = "r+", *args: Any, func: FuncExcept | None = None, **kwargs: Any) -> Any:
    """
    Open file and return a stream. Raise OSError upon failure.

    :param file:        Is either a text or byte string giving the name of the file to be opened.
                        It is also possible to use a string or bytearray as a file for both reading and writing.
                        For strings, StringIO can be used like a file opened in a text mode.
                        For bytes a BytesIO can be used like a file opened in a binary mode.
    :param mode:        This is an optional string that specifies the mode in which the file is opened.
                        It defaults to 'r' which means open for reading in text mode.
                        Other common values are:
                            'w' for writing, and truncating the file if it already exists
                            'x' for creating and writing to a new file
                            'a' for appending, which on some Unix systems means that all writes append to the end
                            of the file regardless of the current seek position).
                        In text mode, if encoding is not specified the encoding used is platform dependent:
                            locale.getpreferredencoding(False) is called to get the current locale encoding.
                        For reading and writing raw bytes use binary mode and leave encoding unspecified.
    :param buffering:   This is an optional integer used to set the buffering policy.
                        Pass:
                            0 to switch buffering off (only allowed in binary mode)
                            1 to select line buffering (only usable in text mode)
                            Integer > 1 to indicate the size of a fixed-size chunk buffer.
                        When no buffering argument is given, the default buffering policy works as follows:
                            Binary files are buffered in fixed-size chunks;
                            the size of the buffer is chosen using a heuristic trying to determine the
                            underlying device's "block size" and falling back on io.DEFAULT_BUFFER_SIZE.
                            On many systems, the buffer will typically be 4096 or 8192 bytes long.
                        "Interactive" text files (files for which isatty() returns True) use line buffering.
                        Other text files use the policy described above for binary files.
    :param: encoding:   This is the name of the encoding used to decode or encode the file.
                        This should only be used in text mode
                        The default encoding is platform dependent, but any encoding supported by Python can be passed.
                        See the codecs module for the list of supported encodings.
    :param newline:     This parameter controls how universal newlines works (it only applies to text mode).
                        It can be None, '', '\n', '\r', and '\r\n'.
                        It works as follows:
                            On input,
                                if newline is None, universal newlines mode is enabled.
                                Lines in the input can end in '\n', '\r', or '\r\n',
                                and these are translated into '\n' before being returned to the caller.
                                If it is '', universal newline mode is enabled, but line endings are
                                returned to the caller untranslated.
                                If it has any of the other legal values, input lines are only terminated
                                by the given string, and the line ending is returned to the caller untranslated.
                            On output,
                                if newline is None, any '\n' characters written are translated to the system default
                                line separator, os.linesep. If newline is '' or '\n', no translation takes place.
                                If newline is any of the other legal values, any '\n' characters written are
                                translated to the given string.

    :return:            A file object whose type depends on the mode, and through which the standard file operations
                        such as reading and writing are performed.
                        When open_file is used to open a file in a text mode ('w', 'r', 'wt', 'rt', etc.),
                            it returns a TextIOWrapper.
                        When used to open a file in a binary mode, the returned class varies:
                            in read binary mode, it returns a BufferedReader
                            in write binary and append binary modes, it returns a BufferedWriter
                            in read/write mode, it returns a BufferedRandom

    """

    check_perms(file, mode, func=func)

    return open(file, mode, *args, errors="strict", closefd=True, **kwargs)  # type: ignore
