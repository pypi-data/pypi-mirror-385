# markdown-heading-numbering

CLI formatter and pre-commit hook that adds hierarchical numbering to Markdown
headings.

______________________________________________________________________

**Table of Contents:**

<!--TOC-->

- [1. Installation](#1-installation)
- [2. CLI Usage](#2-cli-usage)
- [3. Pre-commit Hook](#3-pre-commit-hook)
- [4. Tests](#4-tests)

<!--TOC-->

______________________________________________________________________

## 1. Installation

```bash
pip install .
```

For development:

```bash
pip install -e .[dev]
```

## 2. CLI Usage

```bash
markdown-heading-numbering \
  --start-from-level 2 \
  --end-at-level 5 \
  --initial-numbering 1 \
  docs/README.md
```

Options:

- `--start-from-level` (`int`, default `2`): first heading level to number.
- `--end-at-level` (`int`, default `6`): last heading level to number
  (inclusive).
- `--initial-numbering` (`int`, default `1`): starting value for the top-most
  numbered heading.

Any existing numbering is removed before the formatter applies the new
sequence.

## 3. Pre-commit Hook

This repository ships a `.pre-commit-hooks.yaml` that points to the CLI. Add
the hook to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/jsh9/markdown-heading-numbering
  rev: <commit-or-tag>
  hooks:
    - id: markdown-heading-numbering
      args: ["--start-from-level", "2", "--end-at-level", "4"]
```

The hook shares the same options as the CLI and formats files in place.

## 4. Tests

```bash
pytest
```
