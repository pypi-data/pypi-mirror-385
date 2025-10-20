#!/usr/bin/env bash
# Script: compare-outputs.sh
# Purpose: Compare multiple agent outputs for consistency (mechanical only)
# Subsystem: validation
# Called by: /validation:validate command
# Outputs: JSON comparison report with similarity scores

set -euo pipefail

# --- Configuration ---
RUN_DIR1="${1:-}"
RUN_DIR2="${2:-}"
OUTPUT_FILE="${3:-/tmp/comparison-report.json}"

# --- Usage ---
usage() {
  echo "Usage: $0 <run-dir-1> <run-dir-2> [output-file]"
  echo "   Or: $0 --all <determinism-test-dir> [output-file]"
  echo ""
  echo "Compare outputs from two agent runs for consistency."
  echo ""
  echo "Examples:"
  echo "  $0 /tmp/determinism/run-1 /tmp/determinism/run-2"
  echo "  $0 --all /tmp/determinism-test-123456"
  exit 1
}

# --- Check for --all flag ---
if [ "$RUN_DIR1" = "--all" ] && [ -n "$RUN_DIR2" ]; then
  BASE_DIR="$RUN_DIR2"
  OUTPUT_FILE="${3:-$BASE_DIR/comparison-report.json}"

  echo "[INFO] Comparing all runs in: $BASE_DIR"

  # Find all run directories
  RUN_DIRS=($(find "$BASE_DIR" -maxdepth 1 -type d -name "run-*" | sort))
  NUM_RUNS=${#RUN_DIRS[@]}

  if [ "$NUM_RUNS" -lt 2 ]; then
    echo "❌ Need at least 2 runs to compare"
    exit 1
  fi

  echo "[INFO] Found $NUM_RUNS runs"

  # Compare each pair
  COMPARISONS=()
  TOTAL_SIMILARITY=0
  COMPARISON_COUNT=0

  for ((i=0; i<NUM_RUNS-1; i++)); do
    for ((j=i+1; j<NUM_RUNS; j++)); do
      DIR1="${RUN_DIRS[$i]}"
      DIR2="${RUN_DIRS[$j]}"

      echo "[COMPARE] $(basename $DIR1) vs $(basename $DIR2)"

      # Count files in each
      FILES1=$(find "$DIR1" -type f ! -name "run-metadata.json" | wc -l)
      FILES2=$(find "$DIR2" -type f ! -name "run-metadata.json" | wc -l)

      # Simple similarity: do directories have same number of files?
      if [ "$FILES1" -eq "$FILES2" ]; then
        # Compare file contents (simple diff count)
        DIFF_COUNT=0
        for file1 in $(find "$DIR1" -type f ! -name "run-metadata.json"); do
          filename=$(basename "$file1")
          file2="$DIR2/$filename"

          if [ -f "$file2" ]; then
            if ! diff -q "$file1" "$file2" > /dev/null 2>&1; then
              DIFF_COUNT=$((DIFF_COUNT + 1))
            fi
          else
            DIFF_COUNT=$((DIFF_COUNT + 1))
          fi
        done

        # Calculate similarity percentage
        if [ "$FILES1" -gt 0 ]; then
          MATCHES=$((FILES1 - DIFF_COUNT))
          SIMILARITY=$(echo "scale=1; ($MATCHES / $FILES1) * 100" | bc)
        else
          SIMILARITY=100
        fi
      else
        # Different file counts = lower similarity
        SIMILARITY=0
      fi

      COMPARISONS+=("{\"run1\": \"$(basename $DIR1)\", \"run2\": \"$(basename $DIR2)\", \"similarity\": $SIMILARITY}")
      TOTAL_SIMILARITY=$(echo "$TOTAL_SIMILARITY + $SIMILARITY" | bc)
      COMPARISON_COUNT=$((COMPARISON_COUNT + 1))

      echo "  → Similarity: ${SIMILARITY}%"
    done
  done

  # Calculate average similarity
  AVG_SIMILARITY=$(echo "scale=1; $TOTAL_SIMILARITY / $COMPARISON_COUNT" | bc)

  # Calculate variation (100 - avg_similarity)
  VARIATION=$(echo "scale=1; 100 - $AVG_SIMILARITY" | bc)

  # Determine determinism status
  if (( $(echo "$AVG_SIMILARITY >= 95" | bc -l) )); then
    DETERMINISM_STATUS="excellent"
  elif (( $(echo "$AVG_SIMILARITY >= 85" | bc -l) )); then
    DETERMINISM_STATUS="good"
  elif (( $(echo "$AVG_SIMILARITY >= 70" | bc -l) )); then
    DETERMINISM_STATUS="acceptable"
  else
    DETERMINISM_STATUS="poor"
  fi

  # Generate report
  cat > "$OUTPUT_FILE" <<EOF
{
  "base_dir": "$BASE_DIR",
  "num_runs": $NUM_RUNS,
  "comparisons": [
$(printf '%s' "${COMPARISONS[@]}" | paste -sd ',' -)
  ],
  "average_similarity": $AVG_SIMILARITY,
  "variation": $VARIATION,
  "determinism_status": "$DETERMINISM_STATUS",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

  echo ""
  echo "✅ Comparison complete"
  echo "📊 Average similarity: ${AVG_SIMILARITY}%"
  echo "📈 Variation: ${VARIATION}%"
  echo "🎯 Status: $DETERMINISM_STATUS"
  echo "📄 Report: $OUTPUT_FILE"

  if [ "$DETERMINISM_STATUS" = "poor" ]; then
    exit 1
  else
    exit 0
  fi
fi

# --- Single Pair Comparison ---
if [ -z "$RUN_DIR1" ] || [ -z "$RUN_DIR2" ]; then
  usage
fi

if [ ! -d "$RUN_DIR1" ] || [ ! -d "$RUN_DIR2" ]; then
  echo "❌ One or both run directories do not exist"
  exit 1
fi

echo "[INFO] Comparing: $RUN_DIR1 vs $RUN_DIR2"

# Count files
FILES1=$(find "$RUN_DIR1" -type f ! -name "run-metadata.json" | wc -l)
FILES2=$(find "$RUN_DIR2" -type f ! -name "run-metadata.json" | wc -l)

echo "[INFO] Files in run 1: $FILES1"
echo "[INFO] Files in run 2: $FILES2"

# Compare
if [ "$FILES1" -eq "$FILES2" ]; then
  DIFF_COUNT=0
  DIFFS=()

  for file1 in $(find "$RUN_DIR1" -type f ! -name "run-metadata.json"); do
    filename=$(basename "$file1")
    file2="$RUN_DIR2/$filename"

    if [ -f "$file2" ]; then
      if ! diff -q "$file1" "$file2" > /dev/null 2>&1; then
        DIFF_COUNT=$((DIFF_COUNT + 1))
        DIFFS+=("\"$filename\"")
      fi
    else
      DIFF_COUNT=$((DIFF_COUNT + 1))
      DIFFS+=("\"$filename (missing in run 2)\"")
    fi
  done

  MATCHES=$((FILES1 - DIFF_COUNT))
  SIMILARITY=$(echo "scale=1; ($MATCHES / $FILES1) * 100" | bc)
else
  SIMILARITY=0
  DIFFS=("\"File count mismatch: $FILES1 vs $FILES2\"")
fi

# Generate report
cat > "$OUTPUT_FILE" <<EOF
{
  "run1": "$RUN_DIR1",
  "run2": "$RUN_DIR2",
  "files_run1": $FILES1,
  "files_run2": $FILES2,
  "similarity": $SIMILARITY,
  "differences": [
$(printf '%s' "${DIFFS[@]}" | paste -sd ',' -)
  ],
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "✅ Comparison complete"
echo "📊 Similarity: ${SIMILARITY}%"
echo "📄 Report: $OUTPUT_FILE"

exit 0
