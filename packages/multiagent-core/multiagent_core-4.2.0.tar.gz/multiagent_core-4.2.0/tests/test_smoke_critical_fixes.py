"""Smoke tests for critical bug fixes (menu spam, workflow pollution).

This module contains minimal smoke tests to validate:
- Menu spam fix works in WSL/Windows
- Workflow pollution fix (no _install_github_workflows)
- Version detection system functional

These are targeted tests based on analysis-report.md findings.
"""

import json
import os
import platform
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from rich.console import Console

from multiagent_core.utils.version_detection import (
    _detect_last_used_version,
    _save_current_version,
    _is_major_upgrade,
    _supports_clear,
    _get_version_file,
)
from multiagent_core.init_progress import InitProgress


# ==============================================================================
# Smoke Test 1: Terminal Detection (Menu Spam Fix)
# ==============================================================================

def test_supports_clear_wsl_detection():
    """SMOKE TEST: Verify WSL terminals are detected as not supporting clear.

    Analysis Finding: Menu spam in WSL fixed by detecting WSL and skipping clear()
    Test Strategy: Mock platform.uname() to simulate WSL environment
    Expected: _supports_clear() returns False for WSL
    """
    # Mock WSL environment
    mock_uname = MagicMock()
    mock_uname.release = "5.10.16.3-microsoft-standard-WSL2"

    with patch('platform.uname', return_value=mock_uname):
        result = _supports_clear()

    assert result is False, "WSL should be detected as NOT supporting clear"


def test_supports_clear_windows_detection():
    """SMOKE TEST: Verify Windows terminals are detected as not supporting clear.

    Analysis Finding: Menu spam in Windows fixed by detecting Windows
    Test Strategy: Mock os.name to simulate Windows
    Expected: _supports_clear() returns False for Windows
    """
    with patch('os.name', 'nt'):
        result = _supports_clear()

    assert result is False, "Windows should be detected as NOT supporting clear"


def test_supports_clear_linux():
    """SMOKE TEST: Verify Linux terminals support clear.

    Test Strategy: Mock Linux environment (not WSL)
    Expected: _supports_clear() returns True for standard Linux
    """
    # Mock Linux environment (not WSL)
    mock_uname = MagicMock()
    mock_uname.release = "5.15.0-generic"  # Standard Linux kernel

    with patch('platform.uname', return_value=mock_uname):
        with patch('os.name', 'posix'):
            result = _supports_clear()

    assert result is True, "Standard Linux should support clear"


def test_init_progress_skips_display_in_quiet_mode():
    """SMOKE TEST: Verify InitProgress respects quiet_mode.

    Analysis Finding: quiet_mode parameter added to prevent spam
    Test Strategy: Create InitProgress with quiet_mode=True, verify no display
    Expected: _display_progress() returns early in quiet mode
    """
    # Create mock console
    mock_console = MagicMock(spec=Console)

    progress = InitProgress(console=mock_console, quiet_mode=True)

    # Try to display - should skip due to quiet_mode
    progress._display_progress()

    # Console.clear() should NOT be called in quiet mode
    mock_console.clear.assert_not_called()


def test_init_progress_skips_display_in_wsl():
    """SMOKE TEST: Verify InitProgress skips display when clear not supported.

    Analysis Finding: WSL/Windows environments skip intermediate displays
    Test Strategy: Mock WSL environment, verify no display
    Expected: _display_progress() returns early when _supports_clear() is False
    """
    # Mock WSL environment
    mock_uname = MagicMock()
    mock_uname.release = "5.10.16.3-microsoft-standard-WSL2"

    # Create mock console
    mock_console = MagicMock(spec=Console)

    with patch('platform.uname', return_value=mock_uname):
        progress = InitProgress(console=mock_console, quiet_mode=False)

        # Try to display - should skip due to WSL
        progress._display_progress()

        # Console.clear() should NOT be called in WSL
        mock_console.clear.assert_not_called()


# ==============================================================================
# Smoke Test 2: Workflow Pollution Fix
# ==============================================================================

def test_no_install_workflows_function_in_cli():
    """SMOKE TEST: Verify _install_github_workflows() removed from CLI.

    Analysis Finding: Function deleted to prevent workflow pollution
    Test Strategy: Import cli module, verify function doesn't exist
    Expected: _install_github_workflows not in cli module
    """
    from multiagent_core import cli

    # Function should NOT exist
    assert not hasattr(cli, '_install_github_workflows'), \
        "_install_github_workflows should be removed from cli.py"


# ==============================================================================
# Smoke Test 3: Version Detection System
# ==============================================================================

def test_version_detection_no_previous_version():
    """SMOKE TEST: Verify version detection when no previous install.

    Analysis Finding: _detect_last_used_version() properly handles first-time users
    Test Strategy: Use temp directory, verify None returned when no version.json
    Expected: Returns None for first-time users
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock home directory
        mock_home = Path(tmpdir)

        with patch('pathlib.Path.home', return_value=mock_home):
            result = _detect_last_used_version()

        assert result is None, "Should return None when no previous version"


def test_version_detection_reads_existing_version():
    """SMOKE TEST: Verify version detection reads existing version.json.

    Analysis Finding: _detect_last_used_version() reads version.json correctly
    Test Strategy: Create fake version.json, verify it's read
    Expected: Returns version string from file
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup fake home directory with version.json
        mock_home = Path(tmpdir)
        version_dir = mock_home / ".multiagent"
        version_dir.mkdir(parents=True)
        version_file = version_dir / "version.json"

        # Write fake version data
        version_file.write_text(json.dumps({
            "version": "3.7.0",
            "last_updated": "2025-01-15T10:00:00Z",
            "init_count": 5
        }))

        with patch('pathlib.Path.home', return_value=mock_home):
            result = _detect_last_used_version()

        assert result == "3.7.0", "Should read version from file"


def test_save_version_creates_file():
    """SMOKE TEST: Verify _save_current_version() creates version.json.

    Analysis Finding: Version tracking system creates version.json on init
    Test Strategy: Save version to temp directory, verify file created
    Expected: version.json created with correct structure
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_home = Path(tmpdir)

        with patch('pathlib.Path.home', return_value=mock_home):
            _save_current_version("4.1.0", metadata={"test": True})

            # Verify file exists
            version_file = mock_home / ".multiagent" / "version.json"
            assert version_file.exists(), "version.json should be created"

            # Verify content
            with open(version_file) as f:
                data = json.load(f)

            assert data['version'] == "4.1.0"
            assert data['init_count'] == 1
            assert 'last_updated' in data
            assert data['metadata']['test'] is True


def test_major_upgrade_detection():
    """SMOKE TEST: Verify major version upgrade detection (3.x -> 4.x).

    Analysis Finding: _is_major_upgrade() detects major version bumps
    Test Strategy: Test 3.7.0 -> 4.1.0 upgrade
    Expected: Returns True for major upgrade
    """
    result = _is_major_upgrade("3.7.0", "4.1.0")
    assert result is True, "3.x -> 4.x should be detected as major upgrade"


def test_minor_upgrade_not_major():
    """SMOKE TEST: Verify minor upgrades not flagged as major.

    Analysis Finding: _is_major_upgrade() correctly handles minor bumps
    Test Strategy: Test 4.0.0 -> 4.1.0 upgrade
    Expected: Returns False for minor upgrade
    """
    result = _is_major_upgrade("4.0.0", "4.1.0")
    assert result is False, "4.0.x -> 4.1.x should NOT be major upgrade"


def test_version_tracking_increments_count():
    """SMOKE TEST: Verify init_count increments on each save.

    Analysis Finding: _save_current_version() tracks init_count
    Test Strategy: Save version twice, verify count increments
    Expected: init_count increments from 1 to 2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_home = Path(tmpdir)

        with patch('pathlib.Path.home', return_value=mock_home):
            # First save
            _save_current_version("4.1.0")

            version_file = mock_home / ".multiagent" / "version.json"
            with open(version_file) as f:
                data1 = json.load(f)
            assert data1['init_count'] == 1

            # Second save
            _save_current_version("4.1.0")

            with open(version_file) as f:
                data2 = json.load(f)
            assert data2['init_count'] == 2, "init_count should increment"


# ==============================================================================
# Integration Smoke Test: Menu Spam Prevention
# ==============================================================================

def test_menu_spam_prevention_integration():
    """INTEGRATION SMOKE TEST: Verify complete menu spam prevention flow.

    Analysis Finding: Multi-layered spam prevention (quiet_mode, WSL detection, throttling)
    Test Strategy: Simulate WSL environment with multiple rapid progress updates
    Expected: Display skipped for all intermediate updates
    """
    # Mock WSL environment
    mock_uname = MagicMock()
    mock_uname.release = "5.10.16.3-microsoft-standard-WSL2"

    # Create mock console
    mock_console = MagicMock(spec=Console)

    with patch('platform.uname', return_value=mock_uname):
        progress = InitProgress(console=mock_console, quiet_mode=False)

        # Simulate multiple rapid progress updates (what caused the bug)
        for i in range(38):  # Original bug showed 38 repeated menus
            progress._display_progress()

        # In WSL, console.clear() should NEVER be called
        mock_console.clear.assert_not_called()

        # But final summary should still work (always shown)
        progress.show_final_summary()
        assert mock_console.print.called, "Final summary should be shown"
