#!/usr/bin/env bash
# Script: update-status.sh
# Purpose: Update enhancement status.json file
# Subsystem: enhancement
# Called by: /enhancement:status slash command
# Outputs: Updated status.json file

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
ENHANCEMENT_ID="${2}"
NEW_STATUS="${3}"

# --- Validation ---
if [[ -z "$ENHANCEMENT_ID" || -z "$NEW_STATUS" ]]; then
    echo "❌ Error: Missing required arguments"
    echo "Usage: update-status.sh <project-dir> <id> <status>"
    exit 1
fi

# Validate ID format
if [[ ! "$ENHANCEMENT_ID" =~ ^[0-9]{3}$ ]]; then
    echo "❌ Error: Invalid ID format (expected: 001, 042, etc.)"
    exit 1
fi

# Validate status
VALID_STATUSES="not-started analyzed ready in-progress blocked completed rejected deferred"
if [[ ! " $VALID_STATUSES " =~ " $NEW_STATUS " ]]; then
    echo "❌ Error: Invalid status '$NEW_STATUS'"
    echo "Valid: $VALID_STATUSES"
    exit 1
fi

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

# Find enhancement directory
ENHANCEMENT_DIR=$(find enhancements/ -maxdepth 1 -type d -name "${ENHANCEMENT_ID}-*" 2>/dev/null | head -1)

if [[ -z "$ENHANCEMENT_DIR" ]]; then
    echo "❌ Error: Enhancement $ENHANCEMENT_ID not found"
    exit 1
fi

# Check if status.json exists
if [[ ! -f "${ENHANCEMENT_DIR}/status.json" ]]; then
    echo "❌ Error: status.json not found in $ENHANCEMENT_DIR"
    exit 1
fi

# Get current status
CURRENT_STATUS=$(jq -r '.status' "${ENHANCEMENT_DIR}/status.json" 2>/dev/null || echo "unknown")

echo "[INFO] Updating status: $CURRENT_STATUS → $NEW_STATUS"

# Generate timestamp
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Update status.json
jq --arg status "$NEW_STATUS" \
   --arg timestamp "$TIMESTAMP" \
   '.status = $status | .updated = $timestamp' \
   "${ENHANCEMENT_DIR}/status.json" > "${ENHANCEMENT_DIR}/status.json.tmp"

# Handle status-specific timestamps
case "$NEW_STATUS" in
    "analyzed")
        jq --arg timestamp "$TIMESTAMP" \
           '.analyzed = $timestamp' \
           "${ENHANCEMENT_DIR}/status.json.tmp" > "${ENHANCEMENT_DIR}/status.json.tmp2"
        mv "${ENHANCEMENT_DIR}/status.json.tmp2" "${ENHANCEMENT_DIR}/status.json.tmp"
        ;;
    "in-progress")
        jq --arg timestamp "$TIMESTAMP" \
           '.started = $timestamp' \
           "${ENHANCEMENT_DIR}/status.json.tmp" > "${ENHANCEMENT_DIR}/status.json.tmp2"
        mv "${ENHANCEMENT_DIR}/status.json.tmp2" "${ENHANCEMENT_DIR}/status.json.tmp"
        ;;
    "completed")
        jq --arg timestamp "$TIMESTAMP" \
           '.completed = $timestamp' \
           "${ENHANCEMENT_DIR}/status.json.tmp" > "${ENHANCEMENT_DIR}/status.json.tmp2"
        mv "${ENHANCEMENT_DIR}/status.json.tmp2" "${ENHANCEMENT_DIR}/status.json.tmp"
        ;;
esac

# Replace original file
mv "${ENHANCEMENT_DIR}/status.json.tmp" "${ENHANCEMENT_DIR}/status.json"

echo "✅ Status updated successfully"
echo "   File: ${ENHANCEMENT_DIR}/status.json"
echo "   Status: $NEW_STATUS"
echo "   Timestamp: $TIMESTAMP"

exit 0
