# Copyright 2025 Georges Martin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CLI command for verifying XML signature."""

import json
import sys
from pathlib import Path

import configargparse
from lxml import etree
from rich.console import Console

from pytest_jux.canonicalizer import load_xml
from pytest_jux.verifier import verify_signature

console = Console()
console_err = Console(stderr=True)


def main() -> int:
    """Verify XML digital signature.

    Returns:
        Exit code (0 for valid signature, 1 for invalid/error)
    """
    parser = configargparse.ArgumentParser(
        description="Verify XML digital signature",
        default_config_files=["~/.jux/config", "/etc/jux/config"],
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Input XML file (default: stdin)",
    )

    parser.add_argument(
        "--cert",
        type=Path,
        required=True,
        env_var="JUX_CERT_PATH",
        help="Certificate file (PEM format) [env: JUX_CERT_PATH]",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet mode (no output)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result in JSON format",
    )

    args = parser.parse_args()

    try:
        # Read XML from file or stdin
        if args.input:
            if not args.input.exists():
                if not args.quiet and not args.json:
                    console_err.print(
                        f"[red]Error:[/red] Input file not found: {args.input}"
                    )
                return 1
            tree = load_xml(args.input)
        else:
            xml_content = sys.stdin.read()
            tree = etree.fromstring(xml_content.encode("utf-8"))

        # Read certificate
        if not args.cert.exists():
            if not args.quiet and not args.json:
                console_err.print(
                    f"[red]Error:[/red] Certificate file not found: {args.cert}"
                )
            return 1

        cert = args.cert.read_bytes()

        # Verify signature
        try:
            is_valid = verify_signature(tree, cert)
        except ValueError as e:
            if args.json:
                result = {
                    "valid": False,
                    "error": str(e),
                }
                print(json.dumps(result))
            elif not args.quiet:
                console_err.print(f"[red]Error:[/red] {e}")
            return 1

        # Output result
        if args.json:
            result = {
                "valid": is_valid,
            }
            print(json.dumps(result))
        elif not args.quiet:
            if is_valid:
                console.print("[green]✓[/green] Signature is valid")
            else:
                console.print("[red]✗[/red] Signature is invalid")

        return 0 if is_valid else 1

    except Exception as e:
        if args.json:
            result = {
                "valid": False,
                "error": str(e),
            }
            print(json.dumps(result))
        elif not args.quiet:
            console_err.print(f"[red]Error:[/red] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
