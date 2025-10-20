"""
MCP Registry Management and Migration

Handles MCP server registry setup, migration, and update protection.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple


class MCPRegistryManager:
    """Manages MCP server registry with update protection"""

    def __init__(self):
        self.multiagent_home = Path.home() / ".multiagent"
        self.config_dir = self.multiagent_home / "config"
        self.default_registry_path = self.config_dir / "mcp-servers-registry.default.json"
        self.user_registry_path = self.config_dir / "mcp-servers-registry.json"
        self.old_registry_path = Path.home() / ".claude" / "mcp-servers-registry.json"

    def ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_default_registry(self) -> Dict:
        """
        Get default registry content from package or create minimal version

        Returns default registry structure with standard MCP servers
        """
        return {
            "version": "1.0.0",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "servers": {
                "github": {
                    "type": "stdio",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${MCP_GITHUB_TOKEN}"},
                    "description": "GitHub API integration - PRs, issues, repositories",
                    "category": "standard"
                },
                "postman": {
                    "type": "stdio",
                    "command": "npx",
                    "args": ["@postman/postman-mcp-server"],
                    "env": {"POSTMAN_API_KEY": "${MCP_POSTMAN_API_KEY}"},
                    "description": "API testing and collection management",
                    "category": "standard"
                },
                "memory": {
                    "type": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "env": {},
                    "description": "Persistent conversation memory (local storage)",
                    "category": "standard"
                },
                "playwright": {
                    "type": "stdio",
                    "command": "npx",
                    "args": ["@playwright/mcp@latest"],
                    "env": {},
                    "description": "Browser automation and E2E testing",
                    "category": "standard"
                },
                "context7": {
                    "variants": {
                        "local": {
                            "type": "stdio",
                            "command": "npx",
                            "args": ["-y", "@upstash/context7-mcp"],
                            "env": {"CONTEXT7_API_KEY": "${MCP_CONTEXT7_API_KEY}"},
                            "description": "Up-to-date documentation (local npx)"
                        },
                        "remote": {
                            "type": "http",
                            "url": "https://mcp.context7.com/mcp",
                            "headers": {"CONTEXT7_API_KEY": "${MCP_CONTEXT7_API_KEY}"},
                            "description": "Up-to-date documentation (remote HTTP)"
                        }
                    },
                    "category": "standard",
                    "description": "Up-to-date code documentation for any library/framework"
                },
                "mem0-mcp": {
                    "type": "stdio",
                    "command": "npx",
                    "args": ["-y", "@mem0/mcp"],
                    "env": {"MEM0_API_KEY": "${MCP_MEM0_API_KEY}"},
                    "description": "Mem0 persistent memory and context management",
                    "category": "standard"
                },
                "supabase": {
                    "type": "stdio",
                    "command": "npx",
                    "args": ["@supabase/mcp-server"],
                    "env": {
                        "SUPABASE_URL": "${MCP_SUPABASE_URL}",
                        "SUPABASE_KEY": "${MCP_SUPABASE_KEY}"
                    },
                    "description": "Supabase backend operations",
                    "category": "standard"
                }
            },
            "notes": {
                "purpose": "Framework default registry - DO NOT EDIT",
                "usage": "Restored when user registry is corrupted or missing",
                "env_vars": "All MCP server keys use MCP_* prefix (e.g., ${MCP_GITHUB_TOKEN})",
                "management_commands": {
                    "add": "/mcp:registry add <server-name>",
                    "remove": "/mcp:registry remove <server-name>",
                    "list": "/mcp:registry list",
                    "sync": "/mcp:registry sync-defaults",
                    "reset": "/mcp:registry reset"
                }
            }
        }

    def update_default_registry(self) -> None:
        """
        Update default registry from package

        Always overwrites - this is framework-managed
        """
        self.ensure_config_dir()

        default_content = self.get_default_registry()

        with open(self.default_registry_path, 'w') as f:
            json.dump(default_content, f, indent=2)

    def initialize_user_registry(self) -> Tuple[bool, str]:
        """
        Initialize user registry if it doesn't exist

        Returns:
            Tuple of (was_created, message)
        """
        self.ensure_config_dir()

        if self.user_registry_path.exists():
            return False, "✓ MCP registry preserved (customizations intact)"

        # Copy from default
        if self.default_registry_path.exists():
            shutil.copy(self.default_registry_path, self.user_registry_path)
        else:
            # Create default first
            self.update_default_registry()
            shutil.copy(self.default_registry_path, self.user_registry_path)

        return True, "✓ MCP registry initialized"

    def migrate_from_old_location(self) -> Tuple[bool, Optional[str]]:
        """
        Migrate registry from old location (~/.claude/) to new location

        Returns:
            Tuple of (was_migrated, message)
        """
        if not self.old_registry_path.exists():
            return False, None

        if self.user_registry_path.exists():
            # Both exist - keep new, backup old
            backup_path = self.old_registry_path.with_suffix('.json.old-backup')
            shutil.move(str(self.old_registry_path), str(backup_path))
            return False, f"Old registry backed up to {backup_path}"

        # Only old exists - migrate it
        self.ensure_config_dir()

        # Copy to new location
        shutil.copy(self.old_registry_path, self.user_registry_path)

        # Rename old file
        migrated_path = self.old_registry_path.with_suffix('.json.migrated')
        shutil.move(str(self.old_registry_path), str(migrated_path))

        message = f"""
✅ MCP Registry Migrated

Old location: {self.old_registry_path}
New location: {self.user_registry_path}

Backup saved: {migrated_path}

All /mcp:* commands now use new location.
Your customizations have been preserved.
        """.strip()

        return True, message

    def setup_registry(self, verbose: bool = True) -> Dict[str, str]:
        """
        Complete registry setup with update protection

        Steps:
        1. Update default registry (always)
        2. Initialize user registry if missing
        3. Migrate from old location if needed

        Args:
            verbose: Print status messages

        Returns:
            Dict with status information
        """
        results = {
            "default_updated": False,
            "user_initialized": False,
            "migrated": False,
            "messages": []
        }

        # Step 1: Update default registry (framework-managed)
        self.update_default_registry()
        results["default_updated"] = True
        if verbose:
            print("✓ Default registry updated")

        # Step 2: Check for migration
        was_migrated, migration_msg = self.migrate_from_old_location()
        if was_migrated:
            results["migrated"] = True
            results["messages"].append(migration_msg)
            if verbose:
                print(migration_msg)

        # Step 3: Initialize user registry if needed
        was_created, init_msg = self.initialize_user_registry()
        results["user_initialized"] = was_created
        results["messages"].append(init_msg)
        if verbose:
            print(init_msg)

        return results

    def get_registry_status(self) -> Dict:
        """Get status of registry files"""
        return {
            "default_exists": self.default_registry_path.exists(),
            "user_exists": self.user_registry_path.exists(),
            "old_exists": self.old_registry_path.exists(),
            "default_path": str(self.default_registry_path),
            "user_path": str(self.user_registry_path),
            "old_path": str(self.old_registry_path)
        }

    def reset_user_registry(self) -> Tuple[bool, str]:
        """
        Reset user registry to framework defaults

        Creates backup before resetting

        Returns:
            Tuple of (success, message)
        """
        if not self.user_registry_path.exists():
            return False, "User registry doesn't exist - nothing to reset"

        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = self.user_registry_path.with_suffix(f'.json.backup.{timestamp}')
        shutil.copy(self.user_registry_path, backup_path)

        # Reset to default
        if not self.default_registry_path.exists():
            self.update_default_registry()

        shutil.copy(self.default_registry_path, self.user_registry_path)

        message = f"""
✅ MCP Registry Reset to Defaults

Backup saved: {backup_path}
Registry reset to framework defaults.

To restore: mv {backup_path} {self.user_registry_path}
        """.strip()

        return True, message

    def sync_new_servers_from_default(self) -> Tuple[int, str]:
        """
        Sync new servers from default registry to user registry

        Returns:
            Tuple of (num_added, message)
        """
        if not self.user_registry_path.exists():
            return 0, "User registry doesn't exist - run initialization first"

        if not self.default_registry_path.exists():
            return 0, "Default registry doesn't exist"

        # Load both registries
        with open(self.user_registry_path) as f:
            user_registry = json.load(f)

        with open(self.default_registry_path) as f:
            default_registry = json.load(f)

        # Find new servers
        user_servers = set(user_registry.get("servers", {}).keys())
        default_servers = set(default_registry.get("servers", {}).keys())
        new_servers = default_servers - user_servers

        if not new_servers:
            return 0, "No new servers in default registry"

        # Add new servers
        for server_name in new_servers:
            user_registry["servers"][server_name] = default_registry["servers"][server_name]

        # Update timestamp
        user_registry["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Save updated registry
        with open(self.user_registry_path, 'w') as f:
            json.dump(user_registry, f, indent=2)

        message = f"""
✅ Synced {len(new_servers)} new servers from defaults

Added: {', '.join(sorted(new_servers))}

Use /mcp:list to see all available servers.
        """.strip()

        return len(new_servers), message


def setup_mcp_registry(verbose: bool = True) -> Dict[str, str]:
    """
    Convenience function for registry setup

    Use this in multiagent init command
    """
    manager = MCPRegistryManager()
    return manager.setup_registry(verbose=verbose)


def get_registry_path() -> Path:
    """
    Get the path to the user's MCP registry

    Use this in all /mcp:* slash commands
    """
    return Path.home() / ".multiagent" / "config" / "mcp-servers-registry.json"


def get_default_registry_path() -> Path:
    """Get the path to the default MCP registry"""
    return Path.home() / ".multiagent" / "config" / "mcp-servers-registry.default.json"
