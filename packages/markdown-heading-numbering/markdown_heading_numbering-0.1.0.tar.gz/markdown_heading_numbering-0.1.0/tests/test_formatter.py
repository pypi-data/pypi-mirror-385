from pathlib import Path

import pytest

from markdown_heading_numbering import format_markdown_text
from markdown_heading_numbering.formatter import HeadingNumberingError

DATA_DIR = Path(__file__).parent / 'test_data'
BEFORE_DIR = DATA_DIR / 'before'
AFTER_DIR = DATA_DIR / 'after'


def _read_case(folder: Path, filename: str) -> str:
    return (folder / filename).read_text(encoding='utf-8')


@pytest.mark.parametrize(
    ('case_name', 'options'),
    [
        ('default.md', {}),
        ('start_level_3.md', {'start_from_level': 3, 'initial_numbering': 2}),
        ('end_level_4.md', {'end_at_level': 4}),
        (
            'all_options.md',
            {'start_from_level': 2, 'end_at_level': 4, 'initial_numbering': 5},
        ),
    ],
)
def test_format_markdown_text(case_name: str, options: dict) -> None:
    before = _read_case(BEFORE_DIR, case_name)
    expected = _read_case(AFTER_DIR, case_name)
    assert format_markdown_text(before, **options) == expected


def test_invalid_configuration() -> None:
    with pytest.raises(HeadingNumberingError):
        format_markdown_text('# Title', start_from_level=3, end_at_level=2)
