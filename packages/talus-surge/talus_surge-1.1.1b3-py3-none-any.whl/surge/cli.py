# -*- coding: utf-8 -*-
import sys
import argparse


def __run_worker(args: list[str]) -> None:
    # Insert the project directory to module path.
    from eastwind.lib.path import DIR_ROOT
    sys.path.insert(0, DIR_ROOT)
    from surge.core.worker import main as worker_main
    worker_main(args)


COMMANDS = {
    "worker": __run_worker,
}


def main() -> None:
    # Run the command line interface main.
    parser = argparse.ArgumentParser(
        prog="surge",
        description="Surge - an external background task execution framework for Eastwind."
    )
    parser.add_argument('command', choices=list(COMMANDS.keys()), help="Available commands")
    parser.add_argument('command_args', nargs=argparse.REMAINDER, help='Command arguments')
    args = parser.parse_args()
    # Run the function we expected.
    COMMANDS[args.command](args.command_args)


if __name__ == "__main__":
    main()