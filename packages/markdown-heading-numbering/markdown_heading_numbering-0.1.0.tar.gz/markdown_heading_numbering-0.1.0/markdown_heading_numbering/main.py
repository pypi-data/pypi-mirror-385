"""Command line interface for markdown heading numbering."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import click

from markdown_heading_numbering.formatter import (
    HeadingNumberingError,
    format_paths,
)


def _validate_levels(_: click.Context, __: click.Parameter, value: int) -> int:
    if value < 1 or value > 6:
        raise click.BadParameter('Must be between 1 and 6.')

    return value


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option(
    '--start-from-level',
    callback=_validate_levels,
    default=2,
    show_default=True,
    help='Start numbering from this heading level.',
)
@click.option(
    '--end-at-level',
    callback=_validate_levels,
    default=6,
    show_default=True,
    help='Stop numbering after this heading level.',
)
@click.option(
    '--initial-numbering',
    type=click.IntRange(min=0),
    default=1,
    show_default=True,
    help='Initial number for the top-most numbered heading level.',
)
@click.argument(
    'paths',
    nargs=-1,
    type=click.Path(
        exists=True, dir_okay=False, resolve_path=True, path_type=Path
    ),
)
def main(
        *,
        start_from_level: int,
        end_at_level: int,
        initial_numbering: int,
        paths: Sequence[Path],
) -> None:
    """Add numbering to markdown headings in-place."""
    if not paths:
        raise click.UsageError('No files provided.')

    if end_at_level < start_from_level:
        raise click.BadParameter(
            '--end-at-level must be greater than or'
            ' equal to --start-from-level.',
            param_hint='--end-at-level',
        )

    try:
        changed = format_paths(
            paths,
            start_from_level=start_from_level,
            end_at_level=end_at_level,
            initial_numbering=initial_numbering,
        )
    except HeadingNumberingError as error:
        raise click.ClickException(str(error)) from error

    if changed:
        formatted = ', '.join(str(path) for path in changed)
        click.echo(f'Updated: {formatted}')


if __name__ == '__main__':
    main()
