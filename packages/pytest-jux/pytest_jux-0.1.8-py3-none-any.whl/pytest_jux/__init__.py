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

"""
pytest-jux: A pytest plugin for signing and publishing JUnit XML test reports.

This plugin integrates with pytest to automatically:
1. Sign JUnit XML test reports using XML digital signatures (XMLDSig)
2. Calculate canonical hashes for duplicate detection
3. Publish signed reports to a Jux REST API backend
"""

__version__ = "0.1.5"
__author__ = "Georges Martin"
__email__ = "jrjsmrtn@gmail.com"

# Import plugin hooks when plugin module is available
try:  # pragma: no cover
    from pytest_jux.plugin import pytest_addoption, pytest_configure

    __all__ = ["pytest_addoption", "pytest_configure", "__version__"]
except ImportError:  # pragma: no cover
    # Plugin module not yet implemented
    __all__ = ["__version__"]
