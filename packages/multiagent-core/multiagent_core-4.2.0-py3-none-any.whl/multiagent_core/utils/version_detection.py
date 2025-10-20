"""Version detection and management utilities for multiagent init.

This module provides functionality to:
- Detect previously installed versions
- Track version upgrades
- Determine terminal capabilities for UI rendering
- Save current version information

Version information is stored in ~/.multiagent/version.json
"""

import json
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


def _get_version_file() -> Path:
    """Get path to version tracking file.

    Returns:
        Path to ~/.multiagent/version.json
    """
    return Path.home() / ".multiagent" / "version.json"


def _detect_last_used_version() -> Optional[str]:
    """Detect the last used version of multiagent-core from version.json.

    Returns:
        Version string (e.g., "3.7.0") if found, None if no previous version
    """
    version_file = _get_version_file()

    # No version file means first-time user
    if not version_file.exists():
        return None

    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('version')
    except (json.JSONDecodeError, IOError, KeyError) as e:
        # Corrupted or unreadable file - treat as first-time user
        # Log warning but don't fail
        print(f"Warning: Could not read version file: {e}")
        return None


def _save_current_version(version: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Save current version to version.json file.

    Args:
        version: Version string to save (e.g., "4.1.0")
        metadata: Optional additional metadata to store
    """
    version_file = _get_version_file()

    # Ensure ~/.multiagent directory exists
    version_file.parent.mkdir(parents=True, exist_ok=True)

    # Read existing data to preserve init_count and other fields
    existing_data = {}
    if version_file.exists():
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Corrupted file, start fresh
            pass

    # Build new version data
    init_count = existing_data.get('init_count', 0) + 1
    previous_version = existing_data.get('version')

    version_data = {
        'version': version,
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        'init_count': init_count,
        'metadata': metadata or {}
    }

    # Add platform info to metadata if not already present
    if 'python_version' not in version_data['metadata']:
        version_data['metadata']['python_version'] = platform.python_version()
    if 'platform' not in version_data['metadata']:
        version_data['metadata']['platform'] = platform.platform()

    # Track version upgrades
    if previous_version and previous_version != version:
        version_data['metadata']['previous_version'] = previous_version
        version_data['metadata']['upgrade_date'] = version_data['last_updated']

    # Write to file
    try:
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2)
    except IOError as e:
        # Log warning but don't fail init
        print(f"Warning: Could not save version file: {e}")


def _is_major_upgrade(from_version: str, to_version: str) -> bool:
    """Check if upgrade is a major version bump (e.g., 3.x → 4.x).

    Args:
        from_version: Previous version string (e.g., "3.7.0")
        to_version: Current version string (e.g., "4.1.0")

    Returns:
        True if major version increased, False otherwise
    """
    try:
        # Parse version strings (format: "X.Y.Z")
        from_parts = from_version.split('.')
        to_parts = to_version.split('.')

        # Extract major version (first number)
        from_major = int(from_parts[0])
        to_major = int(to_parts[0])

        # Major upgrade if first number increased
        return to_major > from_major
    except (ValueError, IndexError, AttributeError):
        # Invalid version format - assume not a major upgrade
        return False


def _supports_clear() -> bool:
    """Detect if terminal properly supports clear operations.

    Checks for problematic terminals:
    - WSL (Windows Subsystem for Linux)
    - Windows Command Prompt
    - Windows PowerShell

    Returns:
        True if terminal supports clear, False for WSL/Windows terminals
    """
    # Check for WSL
    uname = platform.uname()
    if 'microsoft' in uname.release.lower() or 'wsl' in uname.release.lower():
        return False

    # Check for Windows
    if os.name == 'nt':
        return False

    # Linux, macOS, and other Unix-like systems generally support clear
    return True
