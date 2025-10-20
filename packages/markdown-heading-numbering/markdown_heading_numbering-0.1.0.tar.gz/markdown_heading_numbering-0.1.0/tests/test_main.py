from pathlib import Path

import pytest
from click.testing import CliRunner

from markdown_heading_numbering.main import main

DATA_DIR = Path(__file__).parent / 'test_data'
BEFORE_DIR = DATA_DIR / 'before'
AFTER_DIR = DATA_DIR / 'after'


def _copy_case(tmp_path: Path, case_name: str) -> Path:
    source = BEFORE_DIR / case_name
    target = tmp_path / case_name
    target.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
    return target


@pytest.mark.parametrize(
    ('case_name', 'cli_args'),
    [
        ('default.md', []),
        (
            'start_level_3.md',
            ['--start-from-level', '3', '--initial-numbering', '2'],
        ),
        ('end_level_4.md', ['--end-at-level', '4']),
        (
            'all_options.md',
            [
                '--start-from-level',
                '2',
                '--end-at-level',
                '4',
                '--initial-numbering',
                '5',
            ],
        ),
    ],
)
def test_cli_formats_files(
        tmp_path: Path, case_name: str, cli_args: list[str]
) -> None:
    runner = CliRunner()
    target = _copy_case(tmp_path, case_name)
    result = runner.invoke(main, [*cli_args, str(target)])
    assert result.exit_code == 0, result.output
    expected = (AFTER_DIR / case_name).read_text(encoding='utf-8')
    assert target.read_text(encoding='utf-8') == expected


def test_cli_rejects_invalid_levels(tmp_path: Path) -> None:
    runner = CliRunner()
    target = _copy_case(tmp_path, 'default.md')
    result = runner.invoke(
        main, ['--start-from-level', '4', '--end-at-level', '3', str(target)]
    )
    assert result.exit_code != 0
    assert (
        '--end-at-level must be greater than or equal to --start-from-level'
        in result.output
    )
