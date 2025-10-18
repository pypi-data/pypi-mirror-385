# Change Log

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-10-17

- Added
  - Skip formatting Jupyter notebooks via `exclude_types: [jupyter]`
- Full diff
  - https://github.com/jsh9/format-json/compare/0.1.0...0.1.1

## [0.1.0] - 2025-10-17

- Added
  - Initial release of `format-json` CLI and pre-commit hook distilled from
    `pretty-format-json`
  - `--no-eof-newline` flag to toggle trailing newline insertion
  - Project scaffolding including tests, tox, muff, and development
    requirements
