# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Gitignore parser configured to work for edk2-pytool-library."""

import collections
import os
import re
import sys
from os.path import abspath, dirname
from pathlib import Path
from typing import Callable, Optional, Union

"""Original file is from
https://github.com/mherrmann/gitignore_parser/blob/master/gitignore_parser.py
sha hash: 1b51ef1f058efc8bcdcb063bf7b16d1394f03fc6

Original License:

MIT License

Copyright (c) 2018 Michael Herrmann
Copyright (c) 2015 Steve Cook

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def handle_negation(file_path: str, rules: list) -> bool:
    """Allows `matched` value override if negation is true.

    Otherwise `matched` cannot be overwritten with an exception.
    Used for ensuring rules with ! will override a previous true result back to false.
    """
    for rule in reversed(rules):
        if rule.match(file_path):
            return not rule.negation
    return False


def parse_gitignore_file(full_path: str, base_dir: Optional[str] = None) -> Callable:
    """Parse a gitignore file."""
    if base_dir is None:
        base_dir = dirname(full_path)
    with open(full_path) as ignore_file:
        lines = ignore_file.readlines()
    return parse_gitignore_lines(lines, full_path, base_dir)


def parse_gitignore_lines(lines: list, full_path: str, base_dir: str) -> Callable:
    """Parse a list of lines matching gitignore syntax."""
    counter = 0
    rules = []
    for line in lines:
        counter += 1
        line = line.rstrip("\n")
        rule = rule_from_pattern(line, base_path=Path(base_dir).resolve(), source=(full_path, counter))
        if rule:
            rules.append(rule)
    if not any(r.negation for r in rules):
        return lambda file_path: any(r.match(file_path) for r in rules)
    else:
        # We have negation rules. We can't use a simple "any" to evaluate them.
        # Later rules override earlier rules.
        return lambda file_path: handle_negation(file_path, rules)


def rule_from_pattern(pattern: str, base_path: Optional[str] = None, source: Optional[str] = None) -> "IgnoreRule":
    """Generates an IgnoreRule object from a pattern.

    Take a .gitignore match pattern, such as "*.py[cod]" or "**/*.bak",
    and return an IgnoreRule suitable for matching against files and
    directories. Patterns which do not match files, such as comments
    and blank lines, will return None.
    Because git allows for nested .gitignore files, a base_path value
    is required for correct behavior. The base path should be absolute.
    """
    if base_path and base_path != Path(base_path).resolve():
        raise ValueError("base_path must be absolute")
    # Store the exact pattern for our repr and string functions
    orig_pattern = pattern
    # Early returns follow
    # Discard comments and separators
    if pattern.strip() == "" or pattern[0] == "#":
        return
    # Strip leading bang before examining double asterisks
    if pattern[0] == "!":
        negation = True
        pattern = pattern[1:]
    else:
        negation = False
    # Multi-asterisks not surrounded by slashes (or at the start/end) should
    # be treated like single-asterisks.
    pattern = re.sub(r"([^/])\*{2,}", r"\1*", pattern)
    pattern = re.sub(r"\*{2,}([^/])", r"*\1", pattern)

    # Special-casing '/', which doesn't match any files or directories
    if pattern.rstrip() == "/":
        return

    directory_only = pattern[-1] == "/"
    # A slash is a sign that we're tied to the base_path of our rule
    # set.
    anchored = "/" in pattern[:-1]
    if pattern[0] == "/":
        pattern = pattern[1:]
    if pattern[0] == "*" and len(pattern) >= 2 and pattern[1] == "*":
        pattern = pattern[2:]
        anchored = False
    if pattern[0] == "/":
        pattern = pattern[1:]
    if pattern[-1] == "/":
        pattern = pattern[:-1]
    # patterns with leading hashes or exclamation marks are escaped with a
    # backslash in front, unescape it
    if pattern[0] == "\\" and pattern[1] in ("#", "!"):
        pattern = pattern[1:]
    # trailing spaces are ignored unless they are escaped with a backslash
    i = len(pattern) - 1
    striptrailingspaces = True
    while i > 1 and pattern[i] == " ":
        if pattern[i - 1] == "\\":
            pattern = pattern[: i - 1] + pattern[i:]
            i = i - 1
            striptrailingspaces = False
        else:
            if striptrailingspaces:
                pattern = pattern[:i]
        i = i - 1
    regex = fnmatch_pathname_to_regex(pattern, directory_only, negation, anchored=bool(anchored))
    return IgnoreRule(
        pattern=orig_pattern,
        regex=regex,
        negation=negation,
        directory_only=directory_only,
        anchored=anchored,
        base_path=_normalize_path(base_path) if base_path else None,
        source=source,
    )


IGNORE_RULE_FIELDS = [
    "pattern",
    "regex",  # Basic values
    "negation",
    "directory_only",
    "anchored",  # Behavior flags
    "base_path",  # Meaningful for gitignore-style behavior
    "source",  # (file, line) tuple for reporting
]


class IgnoreRule(collections.namedtuple("IgnoreRule_", IGNORE_RULE_FIELDS)):
    """Class representing a single rule parsed from a .ignore file."""

    def __str__(self) -> str:
        """String representation (user friendly) of the rule."""
        return self.pattern

    def __repr__(self) -> str:
        """String representation (developer friendly) of the rule."""
        return "".join(["IgnoreRule('", self.pattern, "')"])

    def match(self, abs_path: str) -> bool:
        """Returns True or False if the path matches the rule."""
        matched = False
        if self.base_path:
            try:
                rel_path = _normalize_path(abs_path).relative_to(self.base_path).as_posix()
            except ValueError as e:
                if "is not in the subpath of" in str(e):
                    return False
                else:
                    raise
        else:
            rel_path = _normalize_path(abs_path).as_posix()
        # Path() strips the trailing following symbols on windows, so we need to
        # preserve it: ' ', '.'
        if sys.platform.startswith("win"):
            rel_path += " " * _count_trailing_symbol(" ", abs_path)
            rel_path += "." * _count_trailing_symbol(".", abs_path)
        # Path() strips the trailing slash, so we need to preserve it
        # in case of directory-only negation
        if self.negation and isinstance(abs_path, str) and abs_path[-1] == "/":
            rel_path += "/"
        if rel_path.startswith("./"):
            rel_path = rel_path[2:]
        if re.search(self.regex, rel_path):
            matched = True
        return matched


# Frustratingly, python's fnmatch doesn't provide the FNM_PATHNAME
# option that .gitignore's behavior depends on.
def fnmatch_pathname_to_regex(pattern: str, directory_only: bool, negation: bool, anchored: bool = False) -> str:
    """Implements fnmatch style-behavior, as though with FNM_PATHNAME flagged.

    WARNING: the path seperator will not match shell-style '*' and '.' wildcards.
    """
    i, n = 0, len(pattern)

    seps = [re.escape(os.sep)]
    if os.altsep is not None:
        seps.append(re.escape(os.altsep))
    seps_group = "[" + "|".join(seps) + "]"
    nonsep = r"[^{}]".format("|".join(seps))

    res = []
    while i < n:
        c = pattern[i]
        i += 1
        if c == "*":
            try:
                if pattern[i] == "*":
                    i += 1
                    if i < n and pattern[i] == "/":
                        i += 1
                        res.append("".join(["(.*", seps_group, ")?"]))
                    else:
                        res.append(".*")
                else:
                    res.append("".join([nonsep, "*"]))
            except IndexError:
                res.append("".join([nonsep, "*"]))
        elif c == "?":
            res.append(nonsep)
        elif c == "/":
            res.append(seps_group)
        elif c == "[":
            j = i
            if j < n and pattern[j] == "!":
                j += 1
            if j < n and pattern[j] == "]":
                j += 1
            while j < n and pattern[j] != "]":
                j += 1
            if j >= n:
                res.append("\\[")
            else:
                stuff = pattern[i:j].replace("\\", "\\\\").replace("/", "")
                i = j + 1
                if stuff[0] == "!":
                    stuff = "".join(["^", stuff[1:]])
                elif stuff[0] == "^":
                    stuff = "".join("\\" + stuff)
                res.append("[{}]".format(stuff))
        else:
            res.append(re.escape(c))
    if anchored:
        res.insert(0, "^")
    else:
        res.insert(0, f"(^|{seps_group})")
    if not directory_only:
        res.append("$")
    elif directory_only and negation:
        res.append("/$")
    else:
        res.append("($|\\/)")
    return "".join(res)


def _normalize_path(path: Union[str, Path]) -> Path:
    """Normalize a path without resolving symlinks.

    This is equivalent to `Path.resolve()` except that it does not resolve symlinks.
    Note that this simplifies paths by removing double slashes, `..`, `.` etc. like
    `Path.resolve()` does.
    """
    return Path(abspath(path))


def _count_trailing_symbol(symbol: str, text: str) -> int:
    """Count the number of trailing characters in a string."""
    count = 0
    for char in reversed(str(text)):
        if char == symbol:
            count += 1
        else:
            break
    return count
