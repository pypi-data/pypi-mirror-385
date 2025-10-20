# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""pytest plugin hooks for Jux test report signing and publishing.

This module implements the pytest plugin hooks for capturing JUnit XML
reports, signing them with XMLDSig, and publishing them to the Jux API.
"""

from pathlib import Path

import pytest
from lxml import etree

from pytest_jux.canonicalizer import compute_canonical_hash, load_xml
from pytest_jux.config import ConfigurationManager, StorageMode
from pytest_jux.metadata import capture_metadata
from pytest_jux.signer import load_private_key, sign_xml
from pytest_jux.storage import ReportStorage


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add plugin command-line options.

    Args:
        parser: pytest command-line parser
    """
    group = parser.getgroup("jux", "Jux test report signing and publishing")
    group.addoption(
        "--jux-sign",
        action="store_true",
        default=False,
        help="Enable signing of JUnit XML reports",
    )
    group.addoption(
        "--jux-key",
        action="store",
        default=None,
        help="Path to private key for signing (PEM format)",
    )
    group.addoption(
        "--jux-cert",
        action="store",
        default=None,
        help="Path to X.509 certificate for signing (PEM format, optional)",
    )
    group.addoption(
        "--jux-publish",
        action="store_true",
        default=False,
        help="Publish signed reports to Jux API",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure plugin based on command-line options and configuration files.

    Loads configuration from configuration files and merges with command-line
    options. Command-line options take precedence over configuration files.

    Args:
        config: pytest configuration object

    Raises:
        pytest.UsageError: If configuration is invalid
    """
    # Load configuration from files (CLI > env > files > defaults)
    config_manager = ConfigurationManager()

    # Load from environment variables
    config_manager.load_from_env()

    # Load from config files (in precedence order)
    # User-level config
    user_config = Path.home() / ".jux" / "config"
    if user_config.exists():
        config_manager.load_from_file(user_config)

    # Project-level configs
    project_configs = [Path(".jux.conf"), Path("pytest.ini")]
    for config_file in project_configs:
        if config_file.exists() and config_file.suffix in [".conf", ".ini"]:
            config_manager.load_from_file(config_file)

    # Command-line options override configuration files
    cli_sign = config.getoption("jux_sign")
    cli_key = config.getoption("jux_key")
    cli_cert = config.getoption("jux_cert")
    cli_publish = config.getoption("jux_publish")

    # Merge configuration (CLI takes precedence)
    jux_sign = cli_sign if cli_sign else config_manager.get("jux_sign")
    jux_key = cli_key if cli_key else config_manager.get("jux_key_path")
    jux_cert = cli_cert if cli_cert else config_manager.get("jux_cert_path")
    jux_publish = cli_publish if cli_publish else config_manager.get("jux_publish")

    # Enable plugin if any functionality is requested (CLI or config file)
    jux_enabled = config_manager.get("jux_enabled") or jux_sign or jux_publish

    # Storage configuration (from config files only, no CLI options yet)
    jux_storage_mode = config_manager.get("jux_storage_mode")
    jux_storage_path = config_manager.get("jux_storage_path")

    # Store merged configuration in config object for later use
    config._jux_enabled = jux_enabled  # type: ignore[attr-defined]
    config._jux_sign = jux_sign  # type: ignore[attr-defined]
    config._jux_key_path = jux_key  # type: ignore[attr-defined]
    config._jux_cert_path = jux_cert  # type: ignore[attr-defined]
    config._jux_publish = jux_publish  # type: ignore[attr-defined]
    config._jux_storage_mode = jux_storage_mode  # type: ignore[attr-defined]
    config._jux_storage_path = jux_storage_path  # type: ignore[attr-defined]

    # Validate configuration if plugin is enabled
    if jux_enabled:
        if jux_sign:
            if not jux_key:
                raise pytest.UsageError(
                    "Error: jux_sign is enabled but jux_key_path is not configured. "
                    "Specify --jux-key or set jux_key_path in configuration file."
                )

            # Verify key file exists
            key_path = Path(jux_key)
            if not key_path.exists():
                raise pytest.UsageError(f"Error: Key file not found: {jux_key}")

            # If certificate provided, verify it exists
            if jux_cert:
                cert_path = Path(jux_cert)
                if not cert_path.exists():
                    raise pytest.UsageError(
                        f"Error: Certificate file not found: {jux_cert}"
                    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Sign and store JUnit XML report after test session completes.

    This hook is called after the test session finishes. If the plugin is enabled
    and a JUnit XML report was generated, it:
    1. Signs the report (if signing is enabled)
    2. Captures environment metadata
    3. Stores the report (signed or unsigned) according to storage mode

    Args:
        session: pytest session object
        exitstatus: pytest exit status code
    """
    # Check if plugin is enabled
    if not getattr(session.config, "_jux_enabled", False):
        return

    # Check if JUnit XML report was configured
    xmlpath = getattr(session.config.option, "xmlpath", None)
    if not xmlpath:
        return

    # Load the generated JUnit XML
    xml_path = Path(xmlpath)
    if not xml_path.exists():
        # XML file wasn't generated (no tests ran, etc.)
        return

    # Get configuration
    jux_sign = getattr(session.config, "_jux_sign", False)
    key_path_str = getattr(session.config, "_jux_key_path", None)
    cert_path_str = getattr(session.config, "_jux_cert_path", None)
    storage_mode = getattr(session.config, "_jux_storage_mode", None)
    storage_path = getattr(session.config, "_jux_storage_path", None)

    try:
        tree = load_xml(xml_path)

        # Sign the XML if signing is enabled
        if jux_sign and key_path_str:
            # Load private key
            key = load_private_key(Path(key_path_str))

            # Load certificate if provided
            cert: str | bytes | None = None
            if cert_path_str:
                cert = Path(cert_path_str).read_bytes()

            # Sign the XML
            tree = sign_xml(tree, key, cert)

            # Write signed XML back to file
            with open(xml_path, "wb") as f:
                f.write(
                    etree.tostring(
                        tree,
                        xml_declaration=True,
                        encoding="utf-8",
                        pretty_print=True,
                    )
                )

        # Capture environment metadata
        metadata = capture_metadata()

        # Compute canonical hash
        canonical_hash = compute_canonical_hash(tree)

        # Store the report if storage is configured
        # Only store locally for LOCAL, BOTH, and CACHE modes
        should_store_locally = storage_mode in [
            StorageMode.LOCAL,
            StorageMode.BOTH,
            StorageMode.CACHE,
        ]

        if should_store_locally and storage_path:
            # Convert XML tree to bytes for storage
            xml_bytes = etree.tostring(
                tree, xml_declaration=True, encoding="utf-8", pretty_print=True
            )

            # Initialize storage
            storage = ReportStorage(storage_path=Path(storage_path))

            # Store the report (xml_content expects bytes, metadata expects EnvironmentMetadata object)
            storage.store_report(
                xml_content=xml_bytes, canonical_hash=canonical_hash, metadata=metadata
            )

    except Exception as e:
        # Report error but don't fail the test run
        import warnings

        warnings.warn(f"Failed to process JUnit XML report: {e}", stacklevel=2)
