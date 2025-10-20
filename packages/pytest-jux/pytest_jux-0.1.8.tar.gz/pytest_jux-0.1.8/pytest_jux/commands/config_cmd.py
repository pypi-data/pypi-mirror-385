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

"""Configuration management command for pytest-jux."""

import argparse
import json
import sys
from pathlib import Path

from pytest_jux.config import ConfigSchema, ConfigurationManager


def cmd_list(args: argparse.Namespace) -> int:
    """List all configuration options.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success)
    """
    schema = ConfigSchema.get_schema()

    if args.json:
        # JSON output
        output = {"options": schema}
        print(json.dumps(output, indent=2, default=str))
    else:
        # Text output
        print("Available Configuration Options:")
        print()
        for key, field_info in schema.items():
            field_type = field_info["type"]
            default = field_info["default"]
            description = field_info.get("description", "")

            # Format type
            if field_type == "enum":
                choices = "|".join(field_info.get("choices", []))
                type_str = f"{field_type}:{choices}"
            else:
                type_str = field_type

            # Format default
            if default is None:
                default_str = "(not set)"
            else:
                default_str = f"[default: {default}]"

            print(f"  {key}")
            print(f"    Type:        {type_str}")
            print(f"    Default:     {default_str}")
            if description:
                print(f"    Description: {description}")
            print()

    return 0


def cmd_dump(args: argparse.Namespace) -> int:
    """Dump current effective configuration.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success)
    """
    config = ConfigurationManager()

    # Load from environment
    config.load_from_env()

    # Load from config files (skip non-INI files)
    for config_file in _find_config_files():
        # Only load .conf and .ini files
        if config_file.suffix in [".conf", ".ini"]:
            config.load_from_file(config_file)

    if args.json:
        # JSON output
        dump = config.dump()
        print(json.dumps(dump, indent=2, default=str))
    else:
        # Text output with sources
        print("Current Configuration:")
        print()

        dump_with_sources = config.dump(include_sources=True)
        for key, info in dump_with_sources.items():
            value = info["value"]
            source = info["source"]

            # Format value
            if value is None:
                value_str = "(not set)"
            else:
                value_str = str(value)

            print(f"  {key} = {value_str}")
            print(f"    Source: {source}")
            print()

    return 0


def cmd_view(args: argparse.Namespace) -> int:
    """View configuration file(s).

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    if args.all:
        # View all config files
        config_files = _find_config_files()

        if not config_files:
            print("No configuration files found.")
            return 0

        print("Configuration Files (in precedence order):")
        print()

        for i, config_file in enumerate(config_files, 1):
            exists = config_file.exists()
            status = "✓ exists" if exists else "✗ not found"

            print(f"{i}. {config_file} ({status})")
            if exists:
                print()
                content = config_file.read_text()
                # Indent file content
                for line in content.splitlines():
                    print(f"     {line}")
            print()
    else:
        # View specific file
        if not args.path:
            print("Error: --path required when not using --all", file=sys.stderr)
            return 1

        config_file = Path(args.path)

        if not config_file.exists():
            print(
                f"Error: Configuration file not found: {config_file}", file=sys.stderr
            )
            return 1

        print(f"Configuration File: {config_file}")
        print()
        print(config_file.read_text())

    return 0


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize configuration file.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    if args.path:
        config_file = Path(args.path)
    else:
        # Default to ~/.jux/config
        config_file = Path.home() / ".jux" / "config"

    # Check if file exists
    if config_file.exists() and not args.force:
        print(
            f"Error: Configuration file already exists: {config_file}",
            file=sys.stderr,
        )
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    # Create parent directory if needed
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Generate config content
    if args.template == "full":
        content = _generate_full_template()
    else:
        content = _generate_minimal_template()

    # Write config file
    config_file.write_text(content)

    print(f"Created configuration file: {config_file}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate configuration.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success)
    """
    config = ConfigurationManager()

    # Load from environment
    config.load_from_env()

    # Load from config files (skip non-INI files)
    for config_file in _find_config_files():
        # Only load .conf and .ini files
        if config_file.suffix in [".conf", ".ini"]:
            config.load_from_file(config_file)

    # Validate
    errors = config.validate(strict=args.strict)

    if args.json:
        # JSON output
        output = {
            "valid": len(errors) == 0,
            "warnings": errors,
        }
        print(json.dumps(output, indent=2))
    else:
        # Text output
        if errors:
            print("Configuration Warnings:")
            print()
            for error in errors:
                print(f"  ⚠  {error}")
            print()
            if args.strict:
                print("Configuration has warnings but is valid.")
            else:
                print("Run with --strict to see dependency warnings.")
        else:
            print("✓ Configuration is valid.")

    return 0


def _find_config_files() -> list[Path]:
    """Find configuration files in standard locations.

    Returns:
        List of potential config file paths (in precedence order)
    """
    config_files = []

    # User-level config
    user_config = Path.home() / ".jux" / "config"
    if user_config.exists():
        config_files.append(user_config)

    # Project-level configs (only .conf and .ini for now)
    project_configs = [
        Path(".jux.conf"),
        Path("pytest.ini"),
    ]
    for config_file in project_configs:
        if config_file.exists():
            config_files.append(config_file)

    # System-level config (Linux/Unix)
    system_config = Path("/etc/jux/config")
    if system_config.exists():
        config_files.append(system_config)

    return config_files


def _generate_minimal_template() -> str:
    """Generate minimal configuration template.

    Returns:
        Configuration file content
    """
    return """[jux]
# Enable pytest-jux plugin
enabled = false

# Enable report signing
sign = false

# Storage mode: local|api|both|cache
storage_mode = local

# Enable API publishing
publish = false
"""


def _generate_full_template() -> str:
    """Generate full configuration template with all options.

    Returns:
        Configuration file content
    """
    return """[jux]
# Core Settings
# -------------

# Enable pytest-jux plugin
enabled = false

# Enable report signing (requires key_path)
sign = false

# Enable API publishing (requires api_url)
publish = false

# Storage Settings
# ----------------

# Storage mode:
#   - local: Store locally only (no API publishing)
#   - api:   Publish to API only (no local storage)
#   - both:  Store locally AND publish to API
#   - cache: Store locally, publish when API available (offline queue)
storage_mode = local

# Custom storage directory path (optional)
# storage_path = ~/.local/share/jux/reports

# Signing Settings
# ----------------

# Path to signing key (PEM format)
# key_path = ~/.jux/signing_key.pem

# Path to X.509 certificate (optional)
# cert_path = ~/.jux/signing_key.crt

# API Settings
# ------------

# API endpoint URL
# api_url = https://jux.example.com/api/v1/reports

# API authentication key (use environment variable for security)
# api_key = your-api-key-here
# Or set via environment: JUX_API_KEY=your-api-key
"""


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for config command.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="jux-config",
        description="Manage pytest-jux configuration",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    # List subcommand
    parser_list = subparsers.add_parser("list", help="List all configuration options")
    parser_list.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    # Dump subcommand
    parser_dump = subparsers.add_parser(
        "dump", help="Show current effective configuration"
    )
    parser_dump.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    # View subcommand
    parser_view = subparsers.add_parser("view", help="View configuration file(s)")
    parser_view.add_argument(
        "path",
        nargs="?",
        help="Configuration file path to view",
    )
    parser_view.add_argument(
        "--all",
        action="store_true",
        help="View all configuration files",
    )

    # Init subcommand
    parser_init = subparsers.add_parser("init", help="Initialize configuration file")
    parser_init.add_argument(
        "--path",
        type=str,
        help="Configuration file path (default: ~/.jux/config)",
    )
    parser_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing configuration file",
    )
    parser_init.add_argument(
        "--template",
        choices=["minimal", "full"],
        default="minimal",
        help="Configuration template (default: minimal)",
    )

    # Validate subcommand
    parser_validate = subparsers.add_parser("validate", help="Validate configuration")
    parser_validate.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation (check dependencies)",
    )
    parser_validate.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for config command.

    Args:
        argv: Command-line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 = success, 1 = error, 2 = usage error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 2

    # Dispatch to subcommand handler
    if args.command == "list":
        return cmd_list(args)
    elif args.command == "dump":
        return cmd_dump(args)
    elif args.command == "view":
        return cmd_view(args)
    elif args.command == "init":
        return cmd_init(args)
    elif args.command == "validate":
        return cmd_validate(args)
    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
