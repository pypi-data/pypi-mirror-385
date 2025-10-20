# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for environment metadata capture."""

import json
import re
import sys
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from pytest_jux.metadata import EnvironmentMetadata, capture_metadata


class TestEnvironmentMetadata:
    """Tests for EnvironmentMetadata class."""

    def test_capture_basic_metadata(self) -> None:
        """Should capture basic environment metadata."""
        metadata = capture_metadata()

        assert metadata.hostname is not None
        assert isinstance(metadata.hostname, str)
        assert len(metadata.hostname) > 0

        assert metadata.username is not None
        assert isinstance(metadata.username, str)
        assert len(metadata.username) > 0

        assert metadata.platform is not None
        assert isinstance(metadata.platform, str)
        assert len(metadata.platform) > 0

        assert metadata.python_version is not None
        assert isinstance(metadata.python_version, str)
        assert len(metadata.python_version) > 0

    def test_timestamp_format(self) -> None:
        """Timestamp should be in ISO 8601 format with UTC timezone."""
        metadata = capture_metadata()

        assert metadata.timestamp is not None
        # Should be ISO 8601 format with timezone
        # Example: 2025-10-17T10:30:00+00:00 or 2025-10-17T10:30:00Z
        iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})"
        assert re.match(iso_pattern, metadata.timestamp)

        # Parse and verify it's UTC
        dt = datetime.fromisoformat(metadata.timestamp.replace("Z", "+00:00"))
        assert dt.tzinfo is not None

    def test_pytest_version_captured(self) -> None:
        """Should capture pytest version."""
        metadata = capture_metadata()

        assert metadata.pytest_version is not None
        assert isinstance(metadata.pytest_version, str)
        # Pytest version format: X.Y.Z
        assert re.match(r"\d+\.\d+\.\d+", metadata.pytest_version)

    def test_pytest_jux_version_captured(self) -> None:
        """Should capture pytest-jux version."""
        metadata = capture_metadata()

        assert metadata.pytest_jux_version is not None
        assert isinstance(metadata.pytest_jux_version, str)
        # pytest-jux version format: X.Y.Z
        assert re.match(r"\d+\.\d+\.\d+", metadata.pytest_jux_version)

    def test_python_version_format(self) -> None:
        """Python version should include version number."""
        metadata = capture_metadata()

        # Should contain something like "3.11.14" or similar
        assert re.search(r"3\.\d+\.\d+", metadata.python_version)

    def test_platform_contains_os_info(self) -> None:
        """Platform should contain OS information."""
        metadata = capture_metadata()

        # Should contain OS name (Linux, Darwin/macOS, Windows, etc.)
        platform_lower = metadata.platform.lower()
        assert any(
            os_name in platform_lower
            for os_name in ["linux", "darwin", "macos", "windows"]
        )

    def test_metadata_to_dict(self) -> None:
        """Should convert metadata to dictionary."""
        metadata = capture_metadata()
        data = metadata.to_dict()

        assert isinstance(data, dict)
        assert "hostname" in data
        assert "username" in data
        assert "platform" in data
        assert "python_version" in data
        assert "pytest_version" in data
        assert "pytest_jux_version" in data
        assert "timestamp" in data

    def test_metadata_to_json(self) -> None:
        """Should convert metadata to JSON."""
        metadata = capture_metadata()
        json_str = metadata.to_json()

        assert isinstance(json_str, str)

        # Parse JSON to verify it's valid
        data = json.loads(json_str)
        assert "hostname" in data
        assert "username" in data
        assert "timestamp" in data

    def test_metadata_with_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should capture environment variables when specified."""
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("CI_JOB_ID", "12345")
        monkeypatch.setenv("CI_COMMIT_SHA", "abc123")

        metadata = capture_metadata(
            include_env_vars=["CI", "CI_JOB_ID", "CI_COMMIT_SHA"]
        )

        assert metadata.env is not None
        assert isinstance(metadata.env, dict)
        assert metadata.env["CI"] == "true"
        assert metadata.env["CI_JOB_ID"] == "12345"
        assert metadata.env["CI_COMMIT_SHA"] == "abc123"

    def test_metadata_env_vars_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should handle missing environment variables gracefully."""
        # Request env vars that don't exist
        metadata = capture_metadata(include_env_vars=["NONEXISTENT_VAR"])

        assert metadata.env is not None
        assert isinstance(metadata.env, dict)
        # Missing vars should not be included
        assert "NONEXISTENT_VAR" not in metadata.env

    def test_metadata_env_vars_optional(self) -> None:
        """Environment variables should be optional."""
        metadata = capture_metadata()

        # env should be None or empty dict when not requested
        assert metadata.env is None or metadata.env == {}

    def test_metadata_to_dict_with_env_vars(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Dictionary representation should include env vars."""
        monkeypatch.setenv("CI", "true")

        metadata = capture_metadata(include_env_vars=["CI"])
        data = metadata.to_dict()

        assert "env" in data
        assert data["env"]["CI"] == "true"

    def test_metadata_excludes_none_env(self) -> None:
        """Dictionary should not include env key when env is None."""
        metadata = capture_metadata()
        data = metadata.to_dict()

        # env should not be in dict if None
        if metadata.env is None:
            assert "env" not in data or data["env"] is None

    def test_timestamp_is_recent(self) -> None:
        """Timestamp should be recent (within last few seconds)."""
        metadata = capture_metadata()

        timestamp_dt = datetime.fromisoformat(metadata.timestamp.replace("Z", "+00:00"))
        now = datetime.now(UTC)

        # Timestamp should be within last 10 seconds
        diff = (now - timestamp_dt).total_seconds()
        assert 0 <= diff < 10

    def test_multiple_captures_same_non_time_fields(self) -> None:
        """Multiple captures should have same non-time fields."""
        metadata1 = capture_metadata()
        metadata2 = capture_metadata()

        # Non-time fields should be identical
        assert metadata1.hostname == metadata2.hostname
        assert metadata1.username == metadata2.username
        assert metadata1.platform == metadata2.platform
        assert metadata1.python_version == metadata2.python_version
        assert metadata1.pytest_version == metadata2.pytest_version
        assert metadata1.pytest_jux_version == metadata2.pytest_jux_version

        # Timestamps might differ slightly
        # Just verify both exist
        assert metadata1.timestamp is not None
        assert metadata2.timestamp is not None

    def test_metadata_equality(self) -> None:
        """Should support equality comparison."""
        metadata1 = EnvironmentMetadata(
            hostname="test-host",
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
            env=None,
        )

        metadata2 = EnvironmentMetadata(
            hostname="test-host",
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
            env=None,
        )

        assert metadata1 == metadata2

    def test_metadata_inequality(self) -> None:
        """Should detect differences in metadata."""
        metadata1 = EnvironmentMetadata(
            hostname="test-host-1",
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
            env=None,
        )

        metadata2 = EnvironmentMetadata(
            hostname="test-host-2",  # Different hostname
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
            env=None,
        )

        assert metadata1 != metadata2

    def test_metadata_repr(self) -> None:
        """Should have useful string representation."""
        metadata = capture_metadata()
        repr_str = repr(metadata)

        assert "EnvironmentMetadata" in repr_str
        assert metadata.hostname in repr_str

    def test_env_vars_filtered(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should only capture requested environment variables."""
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("SECRET_TOKEN", "secret123")
        monkeypatch.setenv("PUBLIC_VAR", "public")

        # Only request CI and PUBLIC_VAR
        metadata = capture_metadata(include_env_vars=["CI", "PUBLIC_VAR"])

        assert metadata.env is not None
        assert "CI" in metadata.env
        assert "PUBLIC_VAR" in metadata.env
        # SECRET_TOKEN should not be captured
        assert "SECRET_TOKEN" not in metadata.env

    def test_json_serialization_with_complex_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should correctly serialize complex environment variables."""
        monkeypatch.setenv("COMPLEX_VAR", "value with spaces")
        monkeypatch.setenv("UNICODE_VAR", "unicode: 你好")

        metadata = capture_metadata(include_env_vars=["COMPLEX_VAR", "UNICODE_VAR"])
        json_str = metadata.to_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["env"]["COMPLEX_VAR"] == "value with spaces"
        assert data["env"]["UNICODE_VAR"] == "unicode: 你好"

    def test_direct_dataclass_construction(self) -> None:
        """Should allow direct construction of EnvironmentMetadata."""
        # This tests the dataclass definition itself
        metadata = EnvironmentMetadata(
            hostname="test.example.com",
            username="testuser",
            platform="Linux-5.10.0",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.0",
            timestamp="2025-10-19T10:00:00Z",
            env={"CI": "true"},
        )

        assert metadata.hostname == "test.example.com"
        assert metadata.username == "testuser"
        assert metadata.env == {"CI": "true"}

    def test_dataclass_with_none_env(self) -> None:
        """Should handle None env in dataclass."""
        metadata = EnvironmentMetadata(
            hostname="test.example.com",
            username="testuser",
            platform="Linux-5.10.0",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.0",
            timestamp="2025-10-19T10:00:00Z",
            env=None,
        )

        assert metadata.env is None
        data = metadata.to_dict()
        assert "env" not in data or data.get("env") is None

    def test_pytest_version_attribute_error(self) -> None:
        """Should handle pytest version AttributeError gracefully."""
        # Mock pytest module without __version__ attribute
        import types

        mock_pytest = types.ModuleType("pytest")
        # Don't set __version__ to trigger AttributeError

        with patch.dict(sys.modules, {"pytest": mock_pytest}):
            metadata = capture_metadata()
            # Should default to "unknown" when __version__ is missing
            assert metadata.pytest_version == "unknown"

    def test_pytest_jux_version_attribute_error(self) -> None:
        """Should handle pytest_jux version AttributeError gracefully."""
        # Mock pytest_jux module without __version__ attribute
        import types

        mock_jux = types.ModuleType("pytest_jux")
        # Don't set __version__ to trigger AttributeError

        with patch.dict(sys.modules, {"pytest_jux": mock_jux}):
            metadata = capture_metadata()
            # Should default to "unknown" when __version__ is missing
            assert metadata.pytest_jux_version == "unknown"
