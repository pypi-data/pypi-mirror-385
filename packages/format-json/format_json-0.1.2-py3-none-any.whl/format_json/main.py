# Adapted from https://github.com/pre-commit/pre-commit-hooks/blob/3fed74c572621f74eaffba6603801d153ffe5ce0/pre_commit_hooks/pretty_format_json.py

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from difflib import unified_diff
from json.encoder import (  # type:ignore[attr-defined]
    _make_iterencode,
    encode_basestring,
    encode_basestring_ascii,
)
from typing import Any


class OriginalTokenFloat(float):
    """float subclass that retains the original JSON token verbatim."""

    __slots__ = ('raw',)

    raw: str

    def __new__(cls, value: str) -> OriginalTokenFloat:
        """Instantiate an `OriginalTokenFloat` while storing the raw token."""
        obj = super().__new__(cls, float(value))
        obj.raw = value
        return obj


class DecimalPreservingEncoder(json.JSONEncoder):
    """JSON encoder that keeps high precision floats exactly as provided."""

    def iterencode(self, o: object, _one_shot: bool = False) -> Iterator[str]:
        """Yield encoded chunks while preserving original float lexemes."""
        if self.check_circular:
            markers: dict[int, object] | None = {}
        else:
            markers = None

        if self.ensure_ascii:
            string_encoder = encode_basestring_ascii
        else:
            string_encoder = encode_basestring

        def floatstr(
                value: float,
                allow_nan: bool = self.allow_nan,
                _repr: Callable[..., Any] = repr,
                _inf: float = float('inf'),
                _neginf: float = -float('inf'),
        ) -> str:
            if isinstance(value, OriginalTokenFloat):
                return value.raw

            if value != value:
                text = 'NaN'
            elif value == _inf:
                text = 'Infinity'
            elif value == _neginf:
                text = '-Infinity'
            else:
                return _repr(value)  # type:ignore[no-any-return]

            if not allow_nan:
                raise ValueError(
                    'Out of range float values are not JSON compliant',
                )

            return text

        if self.indent is not None:
            if isinstance(self.indent, str):
                indent_value: str | None = self.indent
            else:
                indent_value = ' ' * self.indent
        else:
            indent_value = None

        _iterencode = _make_iterencode(
            markers,
            self.default,
            string_encoder,
            indent_value,
            floatstr,
            self.key_separator,
            self.item_separator,
            self.sort_keys,
            self.skipkeys,
            _one_shot,
        )
        return _iterencode(o, 0)  # type:ignore[no-any-return]


def _get_pretty_format(
        contents: str,
        indent: str,
        ensure_ascii: bool = True,
        sort_keys: bool = True,
        top_keys: Sequence[str] = (),
        newline_at_end: bool = True,
) -> str:
    """Format JSON string according to the provided options."""

    def pairs_first(pairs: Sequence[tuple[str, str]]) -> Mapping[str, str]:
        before = [pair for pair in pairs if pair[0] in top_keys]
        before = sorted(before, key=lambda x: top_keys.index(x[0]))
        after = [pair for pair in pairs if pair[0] not in top_keys]
        if sort_keys:
            after.sort()

        return dict(before + after)

    json_pretty = json.dumps(
        json.loads(
            contents,
            object_pairs_hook=pairs_first,
            parse_float=OriginalTokenFloat,
        ),
        indent=indent,
        ensure_ascii=ensure_ascii,
        cls=DecimalPreservingEncoder,
    )
    return f'{json_pretty}\n' if newline_at_end else json_pretty


def _autofix(filename: str, new_contents: str) -> None:
    print(f'Fixing file {filename}')
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(new_contents)


def parse_num_to_int(s: str) -> int | str:
    """Convert string numbers to int, leaving strings as is."""
    try:
        return int(s)
    except ValueError:
        return s


def parse_topkeys(s: str) -> list[str]:
    return s.split(',')


def get_diff(source: str, target: str, file: str) -> str:
    source_lines = source.splitlines(True)
    target_lines = target.splitlines(True)
    diff = unified_diff(source_lines, target_lines, fromfile=file, tofile=file)
    return ''.join(diff)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--autofix',
        action='store_true',
        dest='autofix',
        help='Automatically fixes encountered not-pretty-formatted files',
    )
    parser.add_argument(
        '--indent',
        type=parse_num_to_int,
        default='2',
        help=(
            'The number of indent spaces or a string to be used as delimiter'
            ' for indentation level e.g. 4 or "\\t" (Default: 2)'
        ),
    )
    parser.add_argument(
        '--no-ensure-ascii',
        action='store_true',
        dest='no_ensure_ascii',
        default=False,
        help=(
            'Do NOT convert non-ASCII characters to Unicode escape sequences '
            '(\\uXXXX)'
        ),
    )
    parser.add_argument(
        '--no-sort-keys',
        action='store_true',
        dest='no_sort_keys',
        default=False,
        help='Keep JSON nodes in the same order',
    )
    parser.add_argument(
        '--no-eof-newline',
        action='store_true',
        dest='no_eof_newline',
        default=False,
        help='Do not add a trailing newline to the formatted JSON output',
    )
    parser.add_argument(
        '--top-keys',
        type=parse_topkeys,
        dest='top_keys',
        default=[],
        help='Ordered list of keys to keep at the top of JSON hashes',
    )
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    status = 0

    for json_file in args.filenames:
        with open(json_file, encoding='UTF-8') as f:
            contents = f.read()

        try:
            pretty_contents = _get_pretty_format(
                contents,
                args.indent,
                ensure_ascii=not args.no_ensure_ascii,
                sort_keys=not args.no_sort_keys,
                top_keys=args.top_keys,
                newline_at_end=not args.no_eof_newline,
            )
        except ValueError:
            print(
                f'Input File {json_file} is not a valid JSON, consider using '
                'check-json',
            )
            status = 1
        else:
            if contents != pretty_contents:
                if args.autofix:
                    _autofix(json_file, pretty_contents)
                else:
                    diff_output = get_diff(
                        contents,
                        pretty_contents,
                        json_file,
                    )
                    sys.stdout.buffer.write(diff_output.encode())

                status = 1

    return status


if __name__ == '__main__':
    raise SystemExit(main())
