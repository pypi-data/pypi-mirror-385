#!/usr/bin/env python3
import argparse
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
from ejad.static_issue import fix_static_issue, apply_fixed_file

# Version
__version__ = "0.1.9"

def main():
    parser = argparse.ArgumentParser(
        prog="ejd",
        description="EJAD CLI Tool"
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version and exit"
    )

    parser.add_argument("-si", "--static-issue", action="store_true",
                        help="Enable static issue fixing mode.")

    subparsers = parser.add_subparsers(dest="command")

    # fix command
    fix_parser = subparsers.add_parser("fix", help="Analyze and fix static issues in a file (creates -fixed version)")
    fix_parser.add_argument("path", type=str, help="Path to the file to fix")
    fix_parser.add_argument("--ruleset", type=str, default=None,
                            help="Optional path to the rule set file (JSON supported). If omitted you will be prompted.")

    # apply command
    apply_parser = subparsers.add_parser("apply", help="Apply the -fixed version to the original file")
    apply_parser.add_argument("path", type=str, help="Path to the original file (will look for <filename>-fixed.<ext>)")

    args = parser.parse_args()

    if args.static_issue and args.command == "fix":
        fix_static_issue(args.path, rule_path=getattr(args, 'ruleset', None))
    elif args.static_issue and args.command == "apply":
        apply_fixed_file(args.path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
