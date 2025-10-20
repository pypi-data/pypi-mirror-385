"""
Core formatting logic for numbering Markdown headings.

The module exposes helpers to format Markdown text in-memory as well as
convenience utilities for working with filesystem paths.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

_HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.*)$')
_NUMBER_PREFIX_PATTERN = re.compile(
    r'^(?P<number>\d+(?:\.\d+)*)\.\s+(?P<title>.*)$'
)


class HeadingNumberingError(ValueError):
    """Raised when numbering configuration is invalid."""


def format_markdown_text(
        text: str,
        *,
        start_from_level: int = 2,
        end_at_level: int = 6,
        initial_numbering: int = 1,
) -> str:
    """
    Return markdown text with headings renumbered according to configuration.

    Parameters
    ----------
    text : str
        Raw markdown text.
    start_from_level : int, default=2
        Lowest heading level (1-6) that receives numbering. Defaults to level
        2.
    end_at_level : int, default=6
        Highest heading level (1-6) that receives numbering. Defaults to level
        6.
    initial_numbering : int, default=1
        Starting number for the top-most numbered heading level. Subsequent
        headings at the same level increment by one.

    Returns
    -------
    str
        The formatted markdown text
    """
    _validate_configuration(start_from_level, end_at_level, initial_numbering)

    counters = [0] * 7  # 1-based indexing for markdown heading levels
    lines = []

    for raw_line in text.splitlines(keepends=True):
        line_body, newline = _split_newline(raw_line)
        heading_match = _HEADING_PATTERN.match(line_body)
        if not heading_match:
            lines.append(raw_line)
            continue

        hashes, content = heading_match.groups()
        level = len(hashes)
        title = _strip_number_prefix(content)

        if level < start_from_level or level > end_at_level:
            lines.append(f'{hashes} {title}{newline}')
            continue

        numbering = _next_number(
            level, counters, start_from_level, end_at_level, initial_numbering
        )
        numbered_title = f'{numbering} {title}' if title else numbering
        lines.append(f'{hashes} {numbered_title}{newline}')

    return ''.join(lines)


def format_markdown_file(
        path: str | Path,
        *,
        start_from_level: int = 2,
        end_at_level: int = 6,
        initial_numbering: int = 1,
) -> bool:
    """
    Format a Markdown file in place.

    Parameters
    ----------
    path : str | Path
        Path to the Markdown file.
    start_from_level : int, default=2
        Lowest heading level (1-6) that receives numbering.
    end_at_level : int, default=6
        Highest heading level (1-6) that receives numbering.
    initial_numbering : int, default=1
        Initial counter value for the top-most numbered heading level.

    Returns
    -------
    bool
        ``True`` if the file content changed, ``False`` otherwise.
    """
    file_path = Path(path)
    original = file_path.read_text(encoding='utf-8')
    formatted = format_markdown_text(
        original,
        start_from_level=start_from_level,
        end_at_level=end_at_level,
        initial_numbering=initial_numbering,
    )
    if formatted != original:
        file_path.write_text(formatted, encoding='utf-8')
        return True

    return False


def format_paths(
        paths: Iterable[str | Path],
        *,
        start_from_level: int = 2,
        end_at_level: int = 6,
        initial_numbering: int = 1,
) -> list[Path]:
    """
    Format multiple paths, returning the ones that were modified.
    """
    changed: list[Path] = []
    for path in paths:
        path_obj = Path(path)
        if path_obj.is_dir():
            raise HeadingNumberingError(
                f'Expected file but received directory: {path}'
            )

        if format_markdown_file(
            path_obj,
            start_from_level=start_from_level,
            end_at_level=end_at_level,
            initial_numbering=initial_numbering,
        ):
            changed.append(path_obj)

    return changed


def _split_newline(line: str) -> tuple[str, str]:
    if line.endswith('\r\n'):
        return line[:-2], '\r\n'

    if line.endswith('\n') or line.endswith('\r'):
        return line[:-1], line[-1]

    return line, ''


def _strip_number_prefix(content: str) -> str:
    match = _NUMBER_PREFIX_PATTERN.match(content.strip())
    if not match:
        return content.strip()

    return match.group('title').lstrip()


def _next_number(
        level: int,
        counters: list[int],
        start_from_level: int,
        end_at_level: int,
        initial_numbering: int,
) -> str:
    if level < start_from_level or level > end_at_level:
        return ''

    # Ensure parent counters exist
    for current_level in range(start_from_level, level):
        if counters[current_level] == 0:
            counters[current_level] = (
                initial_numbering if current_level == start_from_level else 1
            )

    if level == start_from_level:
        counters[level] = (
            initial_numbering if counters[level] == 0 else counters[level] + 1
        )
    else:
        counters[level] = 1 if counters[level] == 0 else counters[level] + 1

    for reset_level in range(level + 1, len(counters)):
        counters[reset_level] = 0

    active_counters = [
        str(counters[idx])
        for idx in range(start_from_level, level + 1)
        if counters[idx] != 0
    ]
    return '.'.join(active_counters) + '.'


def _validate_configuration(
        start_from_level: int,
        end_at_level: int,
        initial_numbering: int,
) -> None:
    if not 1 <= start_from_level <= 6:
        raise HeadingNumberingError(
            '--start-from-level must be between 1 and 6.'
        )

    if not 1 <= end_at_level <= 6:
        raise HeadingNumberingError('--end-at-level must be between 1 and 6.')

    if end_at_level < start_from_level:
        raise HeadingNumberingError(
            '--end-at-level must be greater than or equal'
            ' to --start-from-level.'
        )

    if initial_numbering < 0:
        raise HeadingNumberingError(
            '--initial-numbering must be zero or positive.'
        )
