#!/usr/bin/env python3

from __future__ import annotations

import argparse

from emmie_server import create_app
from emmie_server.db import database_summary, initialize_database
from emmie_server.shells import SHELL_DEFINITIONS


def build_parser() -> argparse.ArgumentParser:
    shell_choices = sorted(SHELL_DEFINITIONS.keys())
    parser = argparse.ArgumentParser(description="Manage the Emmie server.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-db", help="Create tables and seed the sample rows.")
    init_parser.add_argument("--shell", choices=shell_choices)

    describe_parser = subparsers.add_parser("describe", help="Print a short runtime summary.")
    describe_parser.add_argument("--json", action="store_true", help="Reserved for future use.")
    describe_parser.add_argument("--shell", choices=shell_choices)

    run_parser = subparsers.add_parser("run-dev", help="Run the Flask development server.")
    run_parser.add_argument("--host", default="127.0.0.1")
    run_parser.add_argument("--port", default=8001, type=int)
    run_parser.add_argument("--debug", action="store_true")
    run_parser.add_argument("--shell", choices=shell_choices)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    app = create_app(shell_variant=getattr(args, "shell", None))

    if args.command == "init-db":
        initialize_database(app.config)
        print(f"Initialized database at {app.config['DB_PATH']}")
        return

    if args.command == "describe":
        summary = database_summary(app.config)
        print(f"App name: {app.config['APP_NAME']}")
        print(f"Shell: {app.config['APP_SHELL']}")
        print(f"URL prefix: {app.config['URL_PREFIX'] or '/'}")
        print(f"Database path: {app.config['DB_PATH']}")
        print(f"Sample nodes: {summary['sample_node_count']}")
        return

    if args.command == "run-dev":
        app.run(host=args.host, port=args.port, debug=args.debug)
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
