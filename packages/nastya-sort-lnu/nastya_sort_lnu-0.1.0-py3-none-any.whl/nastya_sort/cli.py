import sys
import click
from typing import Iterable, List, Tuple


def try_float(s: str):
    """Try to convert string to float, return None if fails."""
    try:
        return float(s)
    except Exception:
        return None


def read_lines_from_files(files: List[str]) -> Iterable[str]:
    """Read lines from files or stdin if no files provided."""
    if not files:
        for line in sys.stdin:
            yield line
    else:
        for fname in files:
            if fname == "-":
                for line in sys.stdin:
                    yield line
            else:
                with open(fname, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        yield line


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-r", "--reverse", is_flag=True, default=False, help="Reverse sort order")
@click.option("-n", "--numeric", is_flag=True, default=False, help="Compare according to numeric value")
@click.argument("files", nargs=-1, type=click.Path(exists=False))
def cli(reverse: bool, numeric: bool, files):
    print('my sort processing')
    """
    nastya-sort — lightweight implementation of Unix sort.
    
    Reads from FILE(s) or stdin if none provided. 
    Use -r to reverse, -n for numeric sort.
    """
    lines = list(read_lines_from_files(list(files)))
    
    if numeric:
        # key returns tuple so non-numeric lines sort after numeric ones consistently
        def keyfunc(line: str) -> Tuple[int, object]:
            s = line.rstrip("\n")
            f = try_float(s)
            if f is not None:
                return (0, f)
            else:
                return (1, s)
    else:
        def keyfunc(line: str):
            return line
    
    try:
        lines.sort(key=keyfunc, reverse=reverse)
    except TypeError:
        # fallback: stable string sort if mixed types cause trouble
        lines = sorted(lines, key=lambda l: str(keyfunc(l)), reverse=reverse)
    
    # Output lines as-is
    out = sys.stdout
    for line in lines:
        out.write(line)


if __name__ == "__main__":
    cli()