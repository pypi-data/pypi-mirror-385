# format-json

`format-json` is a JSON formatter that ships both a standalone CLI and a
pre-commit hook. It is adapted from the
[`pretty-format-json`](https://github.com/pre-commit/pre-commit-hooks)
pre-commit hook, with only one difference, as seen below.

**Table of Contents:**

<!--TOC-->

- [1. How does `format-json` differs from `pretty-format-json`?](#1-how-does-format-json-differs-from-pretty-format-json)
- [2. Why a separate project from `pretty-format-json`?](#2-why-a-separate-project-from-pretty-format-json)
- [3. Usage](#3-usage)
  - [3.1. As a command-line tool](#31-as-a-command-line-tool)
  - [3.2. As a pre-commit hook](#32-as-a-pre-commit-hook)
- [4. Instructions for Maintainers](#4-instructions-for-maintainers)

<!--TOC-->

## 1. How does `format-json` differs from `pretty-format-json`?

| Feature                            | format-json | pretty-format-json |
| ---------------------------------- | ----------- | ------------------ |
| Config option for trailing newline | ✅          | ❌                 |

## 2. Why a separate project from `pretty-format-json`?

There are oftentimes practical reasons for JSON files to **not** have a
trailing newline.

But the maintainers of `pretty-format-json`
[hard-coded a newline](https://github.com/pre-commit/pre-commit-hooks/blob/3fed74c572621f74eaffba6603801d153ffe5ce0/pre_commit_hooks/pretty_format_json.py#L30)
at the end of the formatted JSON, and they
[chose not to offer a configuration option for this](https://github.com/pre-commit/pre-commit-hooks/issues/1203).

## 3. Usage

### 3.1. As a command-line tool

First, install it:

```bash
pip install format-json
```

Then, in the terminal, you can do something like:

```bash
format-json --autofix --no-eof-newline path/to/file.json
```

All command-line options from `pretty-format-json` are preserved, with the new
`--no-eof-newline` flag layered on top.

### 3.2. As a pre-commit hook

Add the hook to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/jsh9/format-json
  rev: <LATEST_VERSION>
  hooks:
    - id: format-json
      args: [--autofix, --no-eof-newline]
```

(You can choose your own args.)

## 4. Instructions for Maintainers

- Run `pip install -e .` to install this project in the "editable" mode.
- Run `pip install -r requirements.dev` to install developer dependencies.
- Run `pytest` to execute the automated tests replicated from the upstream
  project.
- Use `tox` to exercise the full test matrix, linting, and formatting targets.
