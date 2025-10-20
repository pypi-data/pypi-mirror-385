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

"""Cache management command for pytest-jux."""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from pytest_jux.storage import ReportStorage, StorageError, get_default_storage_path


def cmd_list(args: argparse.Namespace) -> int:
    """List all cached reports.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        storage_path = (
            Path(args.storage_path) if args.storage_path else get_default_storage_path()
        )
        storage = ReportStorage(storage_path=storage_path)

        reports = storage.list_reports()

        if args.json:
            # JSON output
            report_data = []
            for report_hash in reports:
                try:
                    metadata = storage.get_metadata(report_hash)
                    report_file = storage_path / "reports" / f"{report_hash}.xml"
                    report_data.append(
                        {
                            "hash": report_hash,
                            "timestamp": metadata.timestamp,
                            "hostname": metadata.hostname,
                            "size": report_file.stat().st_size
                            if report_file.exists()
                            else 0,
                        }
                    )
                except StorageError:
                    # Skip reports with missing metadata
                    continue

            output = {"reports": report_data, "total": len(report_data)}
            print(json.dumps(output, indent=2))
        else:
            # Text output
            if not reports:
                print("No cached reports found.")
            else:
                print(f"Cached Reports ({len(reports)} total):")
                print()
                for report_hash in reports:
                    try:
                        metadata = storage.get_metadata(report_hash)
                        print(f"  {report_hash}")
                        print(f"    Timestamp: {metadata.timestamp}")
                        print(f"    Hostname:  {metadata.hostname}")
                        print(f"    Username:  {metadata.username}")
                        print()
                    except StorageError:
                        print(f"  {report_hash} (metadata missing)")
                        print()

        return 0

    except Exception as e:
        print(f"Error listing reports: {e}", file=sys.stderr)
        return 1


def cmd_show(args: argparse.Namespace) -> int:
    """Show details for a specific cached report.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        storage_path = (
            Path(args.storage_path) if args.storage_path else get_default_storage_path()
        )
        storage = ReportStorage(storage_path=storage_path)

        report_hash = args.hash

        # Get report and metadata
        report_xml = storage.get_report(report_hash)
        metadata = storage.get_metadata(report_hash)

        if args.json:
            # JSON output
            output = {
                "hash": report_hash,
                "metadata": metadata.to_dict(),
                "report": report_xml.decode("utf-8"),
                "size": len(report_xml),
            }
            print(json.dumps(output, indent=2))
        else:
            # Text output
            print(f"Report: {report_hash}")
            print()
            print("Metadata:")
            print(f"  Hostname:       {metadata.hostname}")
            print(f"  Username:       {metadata.username}")
            print(f"  Platform:       {metadata.platform}")
            print(f"  Python Version: {metadata.python_version}")
            print(f"  pytest Version: {metadata.pytest_version}")
            print(f"  Timestamp:      {metadata.timestamp}")
            if metadata.env:
                print("  Environment:")
                for key, value in metadata.env.items():
                    print(f"    {key}: {value}")
            print()
            print(f"Report Content ({len(report_xml)} bytes):")
            print(report_xml.decode("utf-8"))

        return 0

    except StorageError:
        print(f"Error: Report not found: {args.hash}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error showing report: {e}", file=sys.stderr)
        return 1


def cmd_stats(args: argparse.Namespace) -> int:
    """Show cache statistics.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success)
    """
    try:
        storage_path = (
            Path(args.storage_path) if args.storage_path else get_default_storage_path()
        )
        storage = ReportStorage(storage_path=storage_path)

        stats = storage.get_stats()

        if args.json:
            # JSON output
            print(json.dumps(stats, indent=2))
        else:
            # Text output
            print("Cache Statistics:")
            print()
            print(f"  Total Reports:  {stats['total_reports']}")
            print(f"  Queued Reports: {stats['queued_reports']}")
            print(f"  Total Size:     {_format_size(stats['total_size'])}")
            if stats["oldest_report"]:
                print(f"  Oldest Report:  {stats['oldest_report']}")
            else:
                print("  Oldest Report:  (none)")

        return 0

    except Exception as e:
        print(f"Error getting statistics: {e}", file=sys.stderr)
        return 1


def cmd_clean(args: argparse.Namespace) -> int:
    """Clean old cached reports.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        storage_path = (
            Path(args.storage_path) if args.storage_path else get_default_storage_path()
        )
        storage = ReportStorage(storage_path=storage_path)

        cutoff_time = datetime.now() - timedelta(days=args.days)
        cutoff_timestamp = cutoff_time.timestamp()

        reports = storage.list_reports()
        reports_to_delete = []

        # Find reports older than cutoff
        for report_hash in reports:
            report_file = storage_path / "reports" / f"{report_hash}.xml"
            if report_file.exists():
                mtime = report_file.stat().st_mtime
                if mtime < cutoff_timestamp:
                    reports_to_delete.append(report_hash)

        if args.dry_run:
            # Dry run - show what would be deleted
            if reports_to_delete:
                print(f"Dry run: Would remove {len(reports_to_delete)} report(s):")
                for report_hash in reports_to_delete:
                    print(f"  {report_hash}")
            else:
                print(f"Dry run: No reports older than {args.days} days found.")
        else:
            # Actually delete
            if reports_to_delete:
                for report_hash in reports_to_delete:
                    storage.delete_report(report_hash)
                print(
                    f"Removed {len(reports_to_delete)} report(s) older than {args.days} days."
                )
            else:
                print(f"No reports older than {args.days} days found.")

        return 0

    except Exception as e:
        print(f"Error cleaning cache: {e}", file=sys.stderr)
        return 1


def _format_size(size_bytes: int) -> str:
    """Format byte size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    size_float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_float < 1024.0:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.1f} PB"


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for cache command.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="jux-cache",
        description="Manage pytest-jux cached reports",
    )

    parser.add_argument(
        "--storage-path",
        type=str,
        help="Custom storage directory path",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    # List subcommand
    parser_list = subparsers.add_parser("list", help="List all cached reports")
    parser_list.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    # Show subcommand
    parser_show = subparsers.add_parser("show", help="Show report details")
    parser_show.add_argument(
        "hash",
        help="Report canonical hash",
    )
    parser_show.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    # Stats subcommand
    parser_stats = subparsers.add_parser("stats", help="Show cache statistics")
    parser_stats.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    # Clean subcommand
    parser_clean = subparsers.add_parser("clean", help="Remove old reports")
    parser_clean.add_argument(
        "--days",
        type=int,
        required=True,
        help="Remove reports older than N days",
    )
    parser_clean.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually deleting",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for cache command.

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
    elif args.command == "show":
        return cmd_show(args)
    elif args.command == "stats":
        return cmd_stats(args)
    elif args.command == "clean":
        return cmd_clean(args)
    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
