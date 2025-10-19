from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def is_interactive() -> bool:
    return sys.stdout.isatty() and sys.stderr.isatty()


class BCOLORS:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def colorize(text: str, color_start: str, color_end: str = BCOLORS.ENDC) -> str:
    if is_interactive():
        return f"{color_start}{text}{color_end}"
    return text


def create_clickable_link(file_path: Path, line: int | None = None) -> str:
    if line is not None:
        return f"{file_path}:{line}"
    return str(file_path)
