"""
PyJolt cli
"""
from typing import Callable
from pathlib import Path

from .new_project import new_project

methods: dict[str, Callable] = {
    "new-project": new_project
}
import argparse

def main():
    parser = argparse.ArgumentParser(prog="pyjolt")
    subparsers = parser.add_subparsers(dest="command")

    new_project_parser = subparsers.add_parser("new-project")
    new_project_parser.add_argument("--name")

    args = parser.parse_args()
    method = methods.get(args.command, None)
    if method is not None:
        args = vars(args)
        del args["command"]
        return method(Path.cwd(), **args)
