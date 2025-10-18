# format-json

`format-json` is a JSON formatter that ships both a standalone CLI and a
pre-commit hook. It is adapted from the
[`pretty-format-json`](https://github.com/pre-commit/pre-commit-hooks)
pre-commit hook, with only one difference, as seen below.

**Table of Contents:**

<!--TOC-->

- [1. `format-json` vs `pretty-format-json`](#1-format-json-vs-pretty-format-json)
- [2. Usage](#2-usage)
  - [2.1. As a command-line tool](#21-as-a-command-line-tool)
  - [2.2. As a pre-commit hook](#22-as-a-pre-commit-hook)
  - [2.3. Configuration options](#23-configuration-options)
- [3. Instructions for Maintainers](#3-instructions-for-maintainers)

<!--TOC-->

## 1. `format-json` vs `pretty-format-json`

| Feature                            | format-json | pretty-format-json                                                                      |
| ---------------------------------- | :---------: | --------------------------------------------------------------------------------------- |
| Config option for trailing newline |     ✅      | ❌ ([Won't implement ever](https://github.com/pre-commit/pre-commit-hooks/issues/1203)) |
| Preserves all digits of floats     |     ✅      | ❌ ([Unresolved since 2022](https://github.com/pre-commit/pre-commit-hooks/issues/780)) |

## 2. Usage

### 2.1. As a command-line tool

First, install it:

```bash
pip install format-json
```

Then, in the terminal, you can do something like:

```bash
format-json --autofix --no-eof-newline path/to/file.json
```

All command-line options from `pretty-format-json` are preserved, with the new
`--no-eof-newline` flag layered on top. See
[Section 2.3](#23-configuration-options) for the complete set of config
options.

### 2.2. As a pre-commit hook

Add the hook to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/jsh9/format-json
  rev: <LATEST_VERSION>
  hooks:
    - id: format-json
      args: [--autofix, --no-eof-newline]
```

(You can choose your own args.)

### 2.3. Configuration options

`format-json` accepts the same options whether invoked via the CLI or
pre-commit. Combine them as needed for your workflow:

- `--autofix` - automatically format json files
- `--indent ...` - Control the indentation (either a number for a number of
  spaces or a string of whitespace). Defaults to 2 spaces.
- `--no-ensure-ascii` preserve unicode characters instead of converting to
  escape sequences
- `--no-sort-keys` - when autofixing, retain the original key ordering (instead
  of sorting the keys)
- `--top-keys comma,separated,keys` - Keys to keep at the top of mappings.
- `--no-eof-newline`: omit the trailing newline (format-json only).

## 3. Instructions for Maintainers

- Run `pip install -e .` to install this project in the "editable" mode.
- Run `pip install -r requirements.dev` to install developer dependencies.
- Run `pytest` to execute the automated tests replicated from the upstream
  project.
- Use `tox` to exercise the full test matrix, linting, and formatting targets.
