#!/usr/bin/env python3
"""
P1.1 Fix: Add timeoutSeconds to all cron jobs in jobs.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration: Job ID -> timeout in seconds
TIMEOUT_CONFIG = {
    "35ba6ee2-19d1-48c2-b7b6-37bb0274998c": 300,   # Evening Briefing - 5 min
    "127744aa-f413-4432-92a1-69dc63caa1dd": 180,   # API Quota Monitor (Evening) - 3 min
    "eb1dc3d5-e75f-49d3-8c38-b87f12f18df6": 300,   # Daily Session Reset - 5 min
    "3039a145-b1a0-4640-bd64-56e0d51c02fe": 600,   # Auto-Update System - 10 min
    "9b5b78c9-1982-4411-ae80-f6d3a9c74ca0": 300,   # Morning Briefing - 5 min
    "d0e66a12-94db-440c-9aec-61af07df32ff": 600,   # Monitor AWS Mac Instance - 10 min
    "9ee86a33-4678-4999-a1e1-0865cee9a672": 180,   # API Quota Monitor (Morning) - 3 min
    "770f3c4e-75bf-4c32-9a29-b23d9bbed080": 300,   # Momotaro iOS Development - 5 min
    "6f1247ea-dcf1-4cc8-875c-6a9b9504c004": 600,   # ReillyDesignStudio Deployment - 10 min
    "c38bdd5e-ef1b-4923-81d8-0b94ff20e911": 900,   # Weekly Memory Consolidation - 15 min
    "8efa9471-3c9c-4a86-96fb-81779fff3e8a": 1200,  # Weekly Leadership Planning - 20 min
    "5c385c77-ce5c-40ee-8f5e-e2e0197c8268": 1200,  # Leidos Leadership Strategy - 20 min
    "ed608174-b89b-4e3f-bada-daf1b4d8f26e": 600,   # Dual Mac Netgear Setup - 10 min
    "78b860fa-338f-4044-97ef-4391694d3f39": 900,   # momo-kiji Content Review - 15 min
    "a4131bed-b5b6-4f43-a32f-de0a5b75b8fa": 600,   # Stripe Environment Setup - 10 min (disabled)
    "102c298e-94bf-49b4-af1b-234b45c33a2f": 300,   # AWS Mac Quota Response Monitor - 5 min (disabled)
}

JOBS_FILE = Path.home() / ".openclaw" / "cron" / "jobs.json"
BACKUP_FILE = Path.home() / ".openclaw" / "cron" / f"jobs.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def main():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║       P1.1 FIX: Add timeoutSeconds to All Cron Jobs           ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    # Check if file exists
    if not JOBS_FILE.exists():
        print(f"❌ ERROR: {JOBS_FILE} not found")
        sys.exit(1)
    
    print(f"📂 Loading jobs file: {JOBS_FILE}")
    
    # Load jobs
    with open(JOBS_FILE, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data['jobs'])} jobs")
    print()
    
    # Create backup
    print(f"💾 Creating backup: {BACKUP_FILE}")
    with open(BACKUP_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Backup created")
    print()
    
    # Add timeoutSeconds to each job
    print("📝 Adding timeoutSeconds to each job:")
    print()
    
    updated_count = 0
    for job in data['jobs']:
        job_id = job.get('id')
        job_name = job.get('name', 'Unknown')
        
        if job_id in TIMEOUT_CONFIG:
            timeout = TIMEOUT_CONFIG[job_id]
            minutes = timeout // 60
            seconds = timeout % 60
            timeout_str = f"{minutes}m{seconds}s"
            
            # Add timeoutSeconds if not already present
            if 'timeoutSeconds' not in job:
                job['timeoutSeconds'] = timeout
                print(f"✅ {job_name}")
                print(f"   ID: {job_id}")
                print(f"   Timeout: {timeout_str} ({timeout}s)")
                updated_count += 1
            else:
                # Already has timeout
                existing = job['timeoutSeconds']
                print(f"⏭️  {job_name} (already has timeout: {existing}s)")
                if existing != timeout:
                    print(f"   Updating: {existing}s → {timeout}s")
                    job['timeoutSeconds'] = timeout
                    updated_count += 1
        else:
            print(f"⚠️  {job_name} - No timeout configured")
        print()
    
    # Write updated jobs
    print("💾 Writing updated jobs.json...")
    with open(JOBS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print("✅ Jobs file updated")
    print()
    
    # Summary
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                        SUMMARY                                 ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"Total jobs processed: {len(data['jobs'])}")
    print(f"Jobs updated with timeoutSeconds: {updated_count}")
    print(f"Backup location: {BACKUP_FILE}")
    print()
    print("✅ P1.1 FIX COMPLETE")
    print()
    print("Next: Reload OpenClaw gateway to apply changes")
    print("  Command: openclaw gateway restart")
    print()

if __name__ == '__main__':
    main()
