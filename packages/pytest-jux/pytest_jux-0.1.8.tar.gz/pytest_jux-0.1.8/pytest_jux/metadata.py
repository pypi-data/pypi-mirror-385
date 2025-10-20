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

"""Environment metadata capture for test reports."""

import getpass
import json
import os
import platform
import socket
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime


@dataclass
class EnvironmentMetadata:
    """Environment metadata for test execution."""

    hostname: str
    username: str
    platform: str
    python_version: str
    pytest_version: str
    pytest_jux_version: str
    timestamp: str
    env: dict[str, str] | None = None

    def to_dict(self) -> dict[str, any]:
        """Convert metadata to dictionary.

        Returns:
            Dictionary representation of metadata
        """
        data = asdict(self)
        # Remove env if None
        if data.get("env") is None:
            data.pop("env", None)
        return data

    def to_json(self, indent: int | None = None) -> str:
        """Convert metadata to JSON string.

        Args:
            indent: JSON indentation level (None for compact)

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)

    def __eq__(self, other: object) -> bool:
        """Check equality with another EnvironmentMetadata instance.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise
        """
        if not isinstance(other, EnvironmentMetadata):
            return NotImplemented

        return (
            self.hostname == other.hostname
            and self.username == other.username
            and self.platform == other.platform
            and self.python_version == other.python_version
            and self.pytest_version == other.pytest_version
            and self.pytest_jux_version == other.pytest_jux_version
            and self.timestamp == other.timestamp
            and self.env == other.env
        )

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation of metadata
        """
        return f"EnvironmentMetadata(hostname={self.hostname!r}, username={self.username!r}, timestamp={self.timestamp!r})"


def capture_metadata(
    include_env_vars: list[str] | None = None,
) -> EnvironmentMetadata:
    """Capture current environment metadata.

    Args:
        include_env_vars: List of environment variable names to capture.
                         If None, no env vars are captured.

    Returns:
        EnvironmentMetadata instance with current environment information
    """
    # Capture basic system information
    hostname = socket.gethostname()
    username = getpass.getuser()
    platform_info = platform.platform()
    python_version = sys.version

    # Capture pytest version
    try:
        import pytest

        pytest_version = pytest.__version__
    except (ImportError, AttributeError):
        pytest_version = "unknown"

    # Capture pytest-jux version
    try:
        from pytest_jux import __version__

        pytest_jux_version = __version__
    except (ImportError, AttributeError):
        pytest_jux_version = "unknown"

    # Generate ISO 8601 timestamp in UTC
    timestamp = datetime.now(UTC).isoformat()

    # Capture requested environment variables
    env_dict: dict[str, str] | None = None
    if include_env_vars:
        env_dict = {}
        for var_name in include_env_vars:
            if var_name in os.environ:
                env_dict[var_name] = os.environ[var_name]
        # Keep empty dict if requested but none found

    return EnvironmentMetadata(
        hostname=hostname,
        username=username,
        platform=platform_info,
        python_version=python_version,
        pytest_version=pytest_version,
        pytest_jux_version=pytest_jux_version,
        timestamp=timestamp,
        env=env_dict,
    )
