import sys
from argparse import ArgumentParser
from pathlib import Path

from jinja2.sandbox import SandboxedEnvironment

from fntpl.template_functions import functions

parser = ArgumentParser(
    prog="fntpl",
    usage="fntpl '<TEMPLATE>'",
    description="The template engine for naming new files.",
)
parser.add_argument("template")
parser.add_argument("--debug", action="store_true")
parser.add_argument(
    "--overwrite", action="store_true", help="Enable file overwrite."
)


def notraceback_excepthook(
    exctype: type[BaseException], value: BaseException, traceback
):
    sys.__excepthook__(exctype, value.with_traceback(None), None)


# Environment for executing untrusted templates.
# https://jinja.palletsprojects.com/en/stable/sandbox/
env = SandboxedEnvironment()


def main():
    args = parser.parse_args()

    if not args.debug:
        sys.excepthook = notraceback_excepthook

    rendered = env.from_string(args.template).render(**functions)
    path = Path(rendered).resolve()

    if not args.overwrite:
        filename = path.stem
        extension = path.suffix

        i = 0
        while path.exists() and i < 9999:
            path = path.parent / f"{filename}-{i}{extension}"
            i += 1
        if path.exists():
            raise StopIteration(f"{path} exists.")

    print(path, end="")


if __name__ == "__main__":
    main()
