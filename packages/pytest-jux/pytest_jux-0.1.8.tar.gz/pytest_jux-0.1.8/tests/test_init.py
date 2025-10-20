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

"""Tests for pytest_jux package initialization."""

import pytest_jux


class TestPackageInit:
    """Tests for package-level attributes and imports."""

    def test_version_defined(self) -> None:
        """Should have __version__ defined."""
        assert hasattr(pytest_jux, "__version__")
        assert isinstance(pytest_jux.__version__, str)
        assert len(pytest_jux.__version__) > 0

    def test_author_defined(self) -> None:
        """Should have __author__ defined."""
        assert hasattr(pytest_jux, "__author__")
        assert isinstance(pytest_jux.__author__, str)

    def test_email_defined(self) -> None:
        """Should have __email__ defined."""
        assert hasattr(pytest_jux, "__email__")
        assert isinstance(pytest_jux.__email__, str)
        assert "@" in pytest_jux.__email__

    def test_all_exports(self) -> None:
        """Should define __all__ with expected exports."""
        assert hasattr(pytest_jux, "__all__")
        assert isinstance(pytest_jux.__all__, list)
        assert "__version__" in pytest_jux.__all__

    def test_pytest_hooks_exported(self) -> None:
        """Should export pytest hooks when available."""
        # If plugin module is available, hooks should be exported
        if "pytest_addoption" in pytest_jux.__all__:
            assert hasattr(pytest_jux, "pytest_addoption")
            assert hasattr(pytest_jux, "pytest_configure")
