import argparse
import math
import re
import shutil
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table


def up(filename):
    console = Console()
    with open(filename) as f:
        markdown = Markdown(f.read())
    console.print(markdown)


def down(filename):
    console = Console()
    with open(filename) as f:
        syntax = Syntax(
            f.read(), "md", theme="monokai", line_numbers=True, word_wrap=True
        )
    console.print(syntax)


def chunkify(lines):
    header = re.compile(r"^ {0,3}(#{1,6})(?:\n|\s+?(.*?)(?:\n|\s+?#+\s*?$))$")
    codefence = re.compile(r"^( {0,3})((?:`|~){3,}) *(\S*)$")
    in_codefence = False
    breakpoints = []
    for i, line in enumerate(lines):
        if re.match(codefence, line):
            in_codefence = not in_codefence
            if in_codefence:
                breakpoints.append(i)
            else:
                breakpoints.append(i + 1)
        if re.match(header, line) and not in_codefence:
            breakpoints.append(i)

    out = []
    for i, start in enumerate(breakpoints):
        try:
            stop = breakpoints[i + 1]
        except IndexError:
            stop = len(lines)
        out.append("".join(lines[start:stop]))

    return out


def sideways(filename):
    console = Console()
    with open(filename) as f:
        chunks = chunkify(f.readlines())
    table = Table(show_header=False, style=Style(bgcolor="#272822"))
    width, _ = shutil.get_terminal_size((80, 20))
    table.add_column("Syntax", width=math.floor(width / 2))
    table.add_column("Markdown", width=math.floor(width / 2))
    for chunk in chunks:
        syntax = Syntax(
            chunk, "md", theme="monokai", line_numbers=False, word_wrap=True
        )
        markdown = Markdown(chunk)
        table.add_row(syntax, markdown)
    console.print(table)


"""def sideways(filename):
    console = Console()
    with open(filename) as f:
        syntax = Syntax(f.read(), "md", theme="monokai", line_numbers=True, word_wrap=True)
        f.seek(0)
        markdown = Markdown(f.read())
    table = Table(show_header=False)
    width, _ = shutil.get_terminal_size((80, 20))
    table.add_column("Syntax", width=math.floor(width/2))
    table.add_column("Markdown", width=math.floor(width/2))
    table.add_row(syntax, markdown)
    console.print(table)"""


def parse_args(args):
    arg_parser = argparse.ArgumentParser(description="Render markdown in the terminal")
    arg_parser.add_argument(
        "direction",
        choices=["up", "down", "sideways"],
        help="Display the markdown file rendered, with syntax highlighting or both side-by-side",
    )
    arg_parser.add_argument("filename", help="Path to a markdown file to render")
    return arg_parser.parse_args(args)


def mark():
    args = parse_args(sys.argv[1:])
    function = getattr(sys.modules[__name__], args.direction)
    function(args.filename)
