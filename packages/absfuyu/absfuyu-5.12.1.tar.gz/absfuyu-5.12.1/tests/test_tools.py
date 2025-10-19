"""
Test: Tools

Version: 5.12.0
Date updated: 17/10/2025 (dd/mm/yyyy)
"""

import pytest

from absfuyu.tools.checksum import Checksum
from absfuyu.tools.shutdownizer import ShutDownizer


# MARK: checksum
@pytest.mark.abs_tools
class TestChecksum:
    """absfuyu.tools.checksum.Checksum"""

    def test_checksum(self) -> None:
        pass


# MARK: shutdownizer
@pytest.mark.abs_tools
class TestShutDownizer:
    """absfuyu.tools.shutdownizer.ShutDownizer"""

    def test_shutdown(self) -> None:
        ins = ShutDownizer()
        assert ins
