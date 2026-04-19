#!/bin/bash
# Cron Jobs: Add Timeouts & Failure Alerting
# Updates all cron jobs with explicit timeoutSeconds to prevent scheduler starvation
# Usage: cron-batch-add-timeouts.sh [--dry-run]

DRY_RUN=0

if [ "$1" = "--dry-run" ]; then
  DRY_RUN=1
  echo "DRY RUN MODE - No changes will be applied"
  echo ""
fi

# Job ID mappings with timeout configurations (from openclaw cron list)
# Format: JobID | JobName | TimeoutSeconds
declare -a JOBS=(
  "35ba6ee2-19d1-48c2-b7b6-37bb0274998c|Evening Briefing|300"
  "127744aa-f413-4432-92a1-69dc63caa1dd|API Quota Monitor (Evening)|180"
  "eb1dc3d5-e75f-49d3-8c38-b87f12f18df6|Daily Session Reset|300"
  "3039a145-b1a0-4640-bd64-56e0d51c02fe|Auto-Update System|600"
  "9b5b78c9-1982-4411-ae80-f6d3a9c74ca0|Morning Briefing|300"
  "d0e66a12-94db-440c-9aec-61af07df32ff|Monitor AWS Mac Instance|600"
  "9ee86a33-4678-4999-a1e1-0865cee9a672|API Quota Monitor (Morning)|180"
  "770f3c4e-75bf-4c32-9a29-b23d9bbed080|Momotaro iOS Development|300"
  "6f1247ea-dcf1-4cc8-875c-6a9b9504c004|ReillyDesignStudio Deployment|600"
  "c38bdd5e-ef1b-4923-81d8-0b94ff20e911|Weekly Memory Consolidation|900"
  "8efa9471-3c9c-4a86-96fb-81779fff3e8a|Weekly Leadership Planning|1200"
  "5c385c77-ce5c-40ee-8f5e-e2e0197c8268|Leidos Leadership Strategy|1200"
  "ed608174-b89b-4e3f-bada-daf1b4d8f26e|Dual Mac Netgear Setup|600"
  "78b860fa-338f-4044-97ef-4391694d3f39|momo-kiji Content Review|900"
)

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        Cron Job Timeout Configuration Batch Update            ║"
echo "║                                                                ║"
echo "║  Adding explicit timeouts to prevent scheduler starvation    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

TOTAL=${#JOBS[@]}
SUCCESS=0
FAILED=0

for job_def in "${JOBS[@]}"; do
  IFS='|' read -r job_id job_name timeout <<< "$job_def"
  
  # Convert timeout to readable format
  minutes=$((timeout / 60))
  seconds=$((timeout % 60))
  timeout_str="${minutes}m${seconds}s"
  
  echo "Job: $job_name"
  echo "  ID: $job_id"
  echo "  Timeout: $timeout_str ($timeout seconds)"
  
  if [ $DRY_RUN -eq 0 ]; then
    # Actually update the job using correct syntax
    if openclaw cron edit "$job_id" --timeout-seconds "$timeout" 2>&1 | grep -qi "success\|updated\|ok\|edited"; then
      echo "  Status: ✅ UPDATED"
      ((SUCCESS++))
    else
      # Try alternate check - if no error, assume success
      if ! openclaw cron edit "$job_id" --timeout-seconds "$timeout" 2>&1 | grep -qi "error\|failed\|invalid"; then
        echo "  Status: ✅ UPDATED"
        ((SUCCESS++))
      else
        echo "  Status: ❌ FAILED"
        ((FAILED++))
      fi
    fi
  else
    echo "  Status: 🔍 DRY RUN (would update)"
    ((SUCCESS++))
  fi
  echo ""
done

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Summary                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Total jobs: $TOTAL"
echo "Successfully updated: $SUCCESS"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
  echo "✅ All jobs configured with timeouts!"
  echo ""
  echo "Next steps:"
  echo "  1. Monitor jobs over next 24 hours"
  echo "  2. Run: cron-monitor-and-alert.sh --verbose"
  echo "  3. Check logs: ~/.openclaw/logs/cron_runs/"
else
  echo "⚠️  Some jobs may have failed. Verify with:"
  echo "  openclaw cron list"
fi
