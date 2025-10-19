#!/usr/bin/env bash
# Script: map-user-data.sh
# Purpose: Map all user data storage locations for GDPR compliance
# Subsystem: compliance
# Called by: /compliance:gdpr-tools slash command
# Outputs: User data map to stdout (JSON format)

set -euo pipefail

# --- Configuration ---
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-/tmp/user-data-map.json}"
USER_ID="${3:-}"  # Optional: map data for specific user

# --- Main Logic ---
cd "$PROJECT_DIR" || exit 1

echo "[INFO] Mapping user data storage locations..."

# TODO: Scan database tables for user-related data
# psql -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';" | \
# while read TABLE; do
#   HAS_USER_ID=$(psql -c "\d $TABLE" | grep -c "user_id\|customer_id\|account_id")
#   if [ $HAS_USER_ID -gt 0 ]; then
#     echo "$TABLE"
#   fi
# done

# TODO: Map user data in Redis/cache
# redis-cli KEYS "user:*" "session:*" "cart:*" | wc -l

# TODO: Find user data in file storage
# find ./uploads ./user-files -type f | head -100

# TODO: Map third-party integrations storing user data
# grep -r "stripe\|sendgrid\|mixpanel\|segment" src/ | grep -oE "[a-z]+\.(com|io)" | sort -u

# TODO: Map data processing activities
# grep -r "export.*user.*data\|backup.*user\|sync.*user" src/ | wc -l

# TODO: If specific user ID provided, map all their data
if [ -n "$USER_ID" ]; then
  echo "[INFO] Mapping data for user: $USER_ID"
  # psql -c "SELECT table_name, COUNT(*) FROM information_schema.columns WHERE table_name IN (SELECT tablename FROM pg_tables) GROUP BY table_name;" | \
  # while read TABLE COUNT; do
  #   RECORDS=$(psql -c "SELECT COUNT(*) FROM $TABLE WHERE user_id = '$USER_ID';" | tail -3 | head -1 | xargs)
  #   echo "$TABLE: $RECORDS records"
  # done
fi

# Placeholder output
cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "user_id": "${USER_ID:-all_users}",
  "data_map": {
    "database": {
      "tables": [],
      "total_records": 0
    },
    "cache": {
      "redis_keys": [],
      "total_keys": 0
    },
    "file_storage": {
      "locations": [],
      "total_files": 0
    },
    "third_party_services": {
      "services": [],
      "data_shared": []
    }
  },
  "processing_activities": {
    "backups": [],
    "exports": [],
    "analytics": []
  },
  "retention_policies": {
    "tables_with_policies": [],
    "tables_without_policies": []
  },
  "gdpr_readiness": {
    "right_to_access": "unknown",
    "right_to_erasure": "unknown",
    "right_to_portability": "unknown",
    "right_to_rectification": "unknown"
  }
}
EOF

echo "✅ User data map written to $OUTPUT_FILE"
exit 0
