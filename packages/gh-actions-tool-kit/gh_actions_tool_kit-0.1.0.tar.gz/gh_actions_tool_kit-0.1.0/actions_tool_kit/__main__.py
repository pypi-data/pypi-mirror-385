from __future__ import annotations

import sys
import argparse
from pathlib import Path
from actions_core import (
    notice, warning, error, debug,
    get_input, set_output, export_variable,
    set_secret, append_summary, group
)

def main() -> int:
    parser = argparse.ArgumentParser(prog="actions_core", description="Tiny @actions/core-style CLI (Python)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_notice = sub.add_parser("notice", help="Emit a notice")
    p_notice.add_argument("message")
    p_notice.add_argument("--title")
    p_notice.add_argument("--file")
    p_notice.add_argument("--line", type=int)
    p_notice.add_argument("--col", type=int)

    p_warn = sub.add_parser("warning", help="Emit a warning")
    p_warn.add_argument("message")
    p_warn.add_argument("--title")
    p_warn.add_argument("--file")
    p_warn.add_argument("--line", type=int)
    p_warn.add_argument("--col", type=int)

    p_err = sub.add_parser("error", help="Emit an error")
    p_err.add_argument("message")
    p_err.add_argument("--title")
    p_err.add_argument("--file")
    p_err.add_argument("--line", type=int)
    p_err.add_argument("--col", type=int)

    p_dbg = sub.add_parser("debug", help="Emit a debug message")
    p_dbg.add_argument("message")

    p_get = sub.add_parser("get-input", help="Read an INPUT_<NAME> env")
    p_get.add_argument("name")
    p_get.add_argument("--required", action="store_true")
    p_get.add_argument("--default")

    p_out = sub.add_parser("set-output", help="Write to $GITHUB_OUTPUT (key=value)")
    p_out.add_argument("pair", help="Format: key=value")

    p_env = sub.add_parser("export", help="Export env var (key=value)")
    p_env.add_argument("pair", help="Format: key=value")

    p_mask = sub.add_parser("mask", help="Mask secret in logs")
    p_mask.add_argument("secret")

    p_sum = sub.add_parser("summary", help="Append a markdown file to step summary")
    p_sum.add_argument("path", type=Path)

    p_group = sub.add_parser("group", help="Wrap stdin/stdout in a collapsible group")
    p_group.add_argument("name")

    args = parser.parse_args()

    if args.cmd == "notice":
        notice(args.message, title=args.title, file=args.file, line=args.line, col=args.col)
    elif args.cmd == "warning":
        warning(args.message, title=args.title, file=args.file, line=args.line, col=args.col)
    elif args.cmd == "error":
        error(args.message, title=args.title, file=args.file, line=args.line, col=args.col)
    elif args.cmd == "debug":
        debug(args.message)
    elif args.cmd == "get-input":
        print(get_input(args.name, required=bool(args.required), default=args.default))
    elif args.cmd == "set-output":
        key, sep, val = args.pair.partition("=")
        if not sep:
            print("set-output requires key=value", file=sys.stderr)
            return 2
        set_output(key, val)
    elif args.cmd == "export":
        key, sep, val = args.pair.partition("=")
        if not sep:
            print("export requires key=value", file=sys.stderr)
            return 2
        export_variable(key, val)
    elif args.cmd == "mask":
        set_secret(args.secret)
    elif args.cmd == "summary":
        append_summary(Path(args.path).read_text(encoding="utf-8"))
    elif args.cmd == "group":
        with group(args.name):
            for line in sys.stdin:
                sys.stdout.write(line)
            sys.stdout.flush()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
