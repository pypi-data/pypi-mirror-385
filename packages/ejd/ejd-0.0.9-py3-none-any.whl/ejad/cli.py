#!/usr/bin/env python3
import argparse
from ejad.static_issue import fix_static_issue

# Version constant
__version__ = "0.0.9"

def main():
    parser = argparse.ArgumentParser(
        prog="ejd",
        description="EJAD CLI Tool ",
        epilog="Example: ejd -si fix myfile.py --ruleset rules.txt"
    )

    parser.add_argument("-si", "--static-issue", action="store_true",
                        help="Enable static issue fixing mode.")
    parser.add_argument("--version", action="version", version=f"ejd {__version__}")

    subparsers = parser.add_subparsers(dest="command", 
                                       help="Available commands",
                                       metavar="{fix}")

    # fix command
    fix_parser = subparsers.add_parser("fix", 
                                       help="Fix static issues in a file using AI analysis")
    fix_parser.add_argument("path", type=str, help="Path to the file to fix")
    fix_parser.add_argument("--ruleset", type=str, default=None,
                            help="Path to rule set file (.txt or .json). If omitted, you will be prompted for the path.")

    args = parser.parse_args()

    if args.static_issue and args.command == "fix":
        # pass optional ruleset path through to the fixer
        fix_static_issue(args.path, rule_path=getattr(args, 'ruleset', None))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
