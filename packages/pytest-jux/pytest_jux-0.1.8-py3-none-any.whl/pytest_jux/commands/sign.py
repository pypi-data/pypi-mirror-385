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

"""jux-sign: Sign JUnit XML reports with XML digital signatures."""

import sys
from pathlib import Path

import configargparse
from lxml import etree
from rich.console import Console

from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml

console = Console()
console_err = Console(stderr=True)


def main() -> int:
    """Main entry point for jux-sign command.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = configargparse.ArgumentParser(
        description="Sign JUnit XML reports with XML digital signatures",
        default_config_files=["~/.jux/config", "/etc/jux/config"],
        formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-c",
        "--config",
        is_config_file=True,
        help="Config file path",
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Input JUnit XML file (default: stdin)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path for signed XML (default: stdout)",
    )

    parser.add_argument(
        "--key",
        type=Path,
        required=True,
        env_var="JUX_KEY_PATH",
        help="Path to private key for signing (PEM format)",
    )

    parser.add_argument(
        "--cert",
        type=Path,
        env_var="JUX_CERT_PATH",
        help="Path to X.509 certificate (PEM format, optional)",
    )

    try:
        args = parser.parse_args()

        # Validate key file exists
        if not args.key.exists():
            console_err.print(f"[red]Error:[/red] Key file not found: {args.key}")
            return 1

        # Validate certificate file if provided
        if args.cert and not args.cert.exists():
            console_err.print(
                f"[red]Error:[/red] Certificate file not found: {args.cert}"
            )
            return 1

        # Determine if we're in quiet mode (outputting to stdout)
        quiet = args.output is None

        # Read input XML
        if args.input:
            # Validate input file exists
            if not args.input.exists():
                console_err.print(
                    f"[red]Error:[/red] Input file not found: {args.input}"
                )
                return 1

            if not quiet:
                console.print(f"[bold]Reading XML:[/bold] {args.input}")
            tree = load_xml(args.input)
        else:
            # Read from stdin
            if not quiet:
                console.print("[bold]Reading XML from stdin...[/bold]")
            xml_content = sys.stdin.read()
            tree = etree.fromstring(xml_content.encode("utf-8"))

        # Load private key
        if not quiet:
            console.print(f"[bold]Loading private key:[/bold] {args.key}")
        key = load_private_key(args.key)

        # Load certificate if provided
        cert: bytes | None = None
        if args.cert:
            if not quiet:
                console.print(f"[bold]Loading certificate:[/bold] {args.cert}")
            cert = args.cert.read_bytes()

        # Sign XML
        if not quiet:
            console.print("[bold]Signing XML...[/bold]")
        signed_tree = sign_xml(tree, key, cert)

        # Serialize signed XML
        signed_xml = etree.tostring(
            signed_tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=True,
        )

        # Write output
        if args.output:
            console.print(f"[bold]Writing signed XML:[/bold] {args.output}")
            args.output.write_bytes(signed_xml)
            console.print("[green]✓[/green] Successfully signed XML")
        else:
            # Write to stdout
            sys.stdout.buffer.write(signed_xml)
            sys.stdout.buffer.flush()

        return 0

    except etree.XMLSyntaxError as e:
        console_err.print(f"[red]XML parsing error:[/red] {e}")
        return 1
    except ValueError as e:
        console_err.print(f"[red]Error:[/red] {e}")
        return 1
    except PermissionError as e:
        console_err.print(f"[red]Permission denied:[/red] {e}")
        return 1
    except Exception as e:
        console_err.print(f"[red]Unexpected error:[/red] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
