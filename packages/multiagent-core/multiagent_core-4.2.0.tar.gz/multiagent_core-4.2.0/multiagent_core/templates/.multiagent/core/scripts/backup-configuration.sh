#!/usr/bin/env bash
# Script: backup-configuration.sh
# Purpose: Create timestamped backup of configuration
# Subsystem: core
# Called by: upgrade-orchestrator agent
# Outputs: Backup file path

set -euo pipefail

CONFIG_FILE="${1:-.multiagent/config.json}"
BACKUP_DIR="${2:-.multiagent/backups}"

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/config.backup.$TIMESTAMP.json"

if [[ ! -f $CONFIG_FILE ]]; then
  echo "❌ ERROR: Config file not found: $CONFIG_FILE"
  exit 1
fi

cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "✅ Backup created: $BACKUP_FILE"
exit 0
