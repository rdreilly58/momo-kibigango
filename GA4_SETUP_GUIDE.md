# GA4 Multi-Property Setup Guide

**Goal:** Get real GA4 data from your three sites (reillydesignstudio, momo-kij, momo-kibidango)

**Status:** GCP credentials installed ✅ | Property IDs needed 🔴

## Current Status

✅ **Done:**
- GCP service account credentials installed at `~/.gcp/credentials.json`
- Multi-property query script created: `scripts/ga4-multi-property.py`
- Configuration structure ready

🔴 **Needed:**
- GA4 Property IDs for each site
- Service account Editor permissions in GA4
- Google Analytics Reporting API enabled in GCP

---

## Step 1: Find Your GA4 Property IDs

For each of your three sites, you need to find the GA4 **Property ID** (numeric).

### For reillydesignstudio.com:
1. Go to https://analytics.google.com
2. Select "reillydesignstudio.com" property
3. Click **Admin** (bottom left)
4. In "Property" column, click **Property Settings**
5. Copy the **Property ID** (looks like: 468246850)
6. Record it here: `PROPERTY_ID_REILLYDESIGNSTUDIO = "123456789"`

### For momo-kij (Blog):
1. Go to https://analytics.google.com
2. Select your momo-kij property
3. Follow same steps as above
4. Record: `PROPERTY_ID_MOMO_KIJ = "987654321"`

### For momo-kibidango.org:
1. Go to https://analytics.google.com
2. Select your momo-kibidango property
3. Follow same steps as above
4. Record: `PROPERTY_ID_MOMO_KIBIDANGO = "456789123"`

---

## Step 2: Update Property IDs in Script

Once you have the property IDs, update them in the script:

**File:** `~/.openclaw/workspace/scripts/ga4-multi-property.py`

**Lines to update (around line 30):**

```python
GA4_PROPERTIES = {
    "reillydesignstudio": {
        "property_id": "468246850",  # ← UPDATE THIS
        "domain": "reillydesignstudio.com",
        "description": "Robert Reilly Design Studio",
    },
    "momo-kij": {
        "property_id": "468246851",  # ← UPDATE THIS
        "domain": "momo-kij.vercel.app",
        "description": "Momotaro Kiji (Blog)",
    },
    "momo-kibidango": {
        "property_id": "468246852",  # ← UPDATE THIS
        "domain": "momo-kibidango.org",
        "description": "Momotaro Kibidango (Portfolio)",
    },
}
```

---

## Step 3: Verify Service Account Permissions

The service account needs **Editor** access to each GA4 property.

### Check/Grant Permissions:
1. Go to https://analytics.google.com
2. Select first property (reillydesignstudio)
3. Click **Admin** → **Property Settings**
4. Scroll to **Property Users**
5. Look for your service account email (from credentials.json)
6. If not listed or not "Editor", add it:
   - Click **+ Add users**
   - Paste service account email (from `.gcp/credentials.json`)
   - Select **Editor** role
   - Save

**Repeat for all three properties.**

---

## Step 4: Enable Google Analytics Reporting API

1. Go to https://console.cloud.google.com
2. Search for "Google Analytics Reporting API"
3. Click **Enable**
4. Done! (The API is now active for your GCP project)

---

## Step 5: Test the Script

Once property IDs are updated:

```bash
# Test with last 7 days
python3 ~/.openclaw/workspace/scripts/ga4-multi-property.py

# Test with specific date range
python3 ~/.openclaw/workspace/scripts/ga4-multi-property.py --days 30

# Get JSON output
python3 ~/.openclaw/workspace/scripts/ga4-multi-property.py --json

# Get CSV output
python3 ~/.openclaw/workspace/scripts/ga4-multi-property.py --format csv
```

---

## Step 6: Integrate with Briefing

Once working, add to daily briefing:

**File:** `~/.openclaw/workspace/skills/daily-briefing/scripts/morning-briefing.sh`

Add this section:

```bash
# GA4 Analytics
echo "<h2>Analytics</h2>" >> "$HTML_FILE"
python3 ~/.openclaw/workspace/scripts/ga4-multi-property.py --format html >> "$HTML_FILE"
```

---

## Troubleshooting

### "Property not found" error
- Check property ID is correct (should be numeric only)
- Verify service account has Editor access to that property

### "403 Unauthorized" error
- Service account doesn't have permission to the property
- Go back to Step 3 and grant Editor access

### "API not enabled" error
- Go to Step 4 and enable Google Analytics Reporting API in GCP

### "Credentials not found" error
- Verify `~/.gcp/credentials.json` exists
- Check permissions: `ls -la ~/.gcp/credentials.json` (should be 600)

---

## Files Created

- **Script:** `scripts/ga4-multi-property.py` (ready to use)
- **Config:** Property IDs (embedded in script, needs updating)
- **Credentials:** `~/.gcp/credentials.json` (already installed)

---

## Expected Output (Once Working)

```
================================================================================
GA4 ANALYTICS — MULTI-PROPERTY REPORT
Generated: 2026-03-27 21:10:00
================================================================================

AGGREGATE METRICS (All Properties)
--------------------------------------------------------------------------------
Total Users:           3,500
Total New Users:       850
Total Sessions:        6,200
Total Page Views:      28,000

PER-PROPERTY BREAKDOWN
--------------------------------------------------------------------------------

Robert Reilly Design Studio (reillydesignstudio.com)
  Users:        1250
  New Users:     340
  Sessions:     2100
  Page Views:   8950
  Avg Duration: 245.0s

Momotaro Kiji (Blog) (momo-kij.vercel.app)
  Users:        1100
  New Users:     300
  Sessions:     1850
  Page Views:   7500
  Avg Duration: 210.0s

Momotaro Kibidango (Portfolio) (momo-kibidango.org)
  Users:        1150
  New Users:     210
  Sessions:     2250
  Page Views:  11550
  Avg Duration: 290.0s

================================================================================
```

---

## Next Steps

1. **Find and record your 3 GA4 Property IDs** (Step 1)
2. **Update the script** with those IDs (Step 2)
3. **Grant permissions** to service account (Step 3)
4. **Enable API** in GCP (Step 4)
5. **Test the script** (Step 5)
6. **Integrate with briefing** (Step 6 - optional)

**Estimated time:** 15-20 minutes

---

## Quick Reference

**Property ID locations:**
- Google Analytics → Admin → Property Settings → Property ID

**Service account email:**
- In `.gcp/credentials.json` under "client_email"

**Script location:**
- `~/.openclaw/workspace/scripts/ga4-multi-property.py`

**Credentials location:**
- `~/.gcp/credentials.json` (already there)

---

**Once complete:** You'll get real-time GA4 data across all three sites in a unified report! 📊
