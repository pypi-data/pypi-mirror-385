#!/usr/bin/env python3
import argparse
from ejad.static_issue import fix_static_issue

def main():
    parser = argparse.ArgumentParser(
        prog="ejd",
        description="EJAD CLI Tool"
    )

    parser.add_argument("-si", "--static-issue", action="store_true",
                        help="Enable static issue fixing mode.")

    subparsers = parser.add_subparsers(dest="command")

    # fix command
    fix_parser = subparsers.add_parser("fix", help="Fix static issue in a file")
    fix_parser.add_argument("path", type=str, help="Path to the file to fix")
    fix_parser.add_argument("--ruleset", type=str, default=None,
                            help="Optional path to the rule set file (JSON supported). If omitted you will be prompted.")
    fix_parser.add_argument("--apply", action="store_true",
                            help="If set, automatically apply fixes to the original file without prompting.")

    args = parser.parse_args()

    if args.static_issue and args.command == "fix":
        # pass optional ruleset path and apply flag through to the fixer
        fix_static_issue(args.path, rule_path=getattr(args, 'ruleset', None), apply=getattr(args, 'apply', False))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
