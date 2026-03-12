# How to Link GA4 to BigQuery - Step-by-Step

## Location: Google Analytics 4 Console

### Step 1: Go to Admin
1. Open: https://analytics.google.com/
2. Select property: **ReillyDesignStudio** (526836321)
3. Click: **⚙️ Admin** (bottom left)

### Step 2: Find Data Streams
1. In Admin, left panel → **Data collection and modification**
2. Click: **Data streams**
3. You should see: **Your website** (or similar)
4. Click on it

### Step 3: Look for Google Cloud Linking
In the data stream details, scroll down until you see:
- **Linking settings** or **Google Cloud linking** section
- OR a card that says **"Link Google Cloud project"** or **"Link BigQuery"**

### Step 4: Click Link BigQuery
1. Click the **Link** button (or **"Link Google Cloud project"**)
2. A dialog will appear asking: **"Select a Google Cloud project"**
3. Choose: **rds-analytics-489420**
4. Click: **Link**

### Step 5: Confirm
You should see:
- ✅ "Successfully linked to BigQuery"
- Project: rds-analytics-489420
- Status: Active

---

## If You Don't See "Google Cloud Linking" Section

This might mean:
1. **Already linked** — Check if there's a "Linked" or "Active" status displayed
2. **Different location** — Look under:
   - Admin → **Integrations** (if that option exists)
   - Admin → **Data streams** → Your stream → Scroll further down
   - Admin → **Export settings**

3. **Admin menu** — Try clicking directly on the data stream name and look for "Linking" tab

---

## Alternative: Link via Google Cloud Console

If you can't find it in GA4:

1. Go to: https://console.cloud.google.com/
2. Project: **rds-analytics-489420**
3. Search: **Analytics Hub** or **Linked Datasets**
4. Look for: **GA4 → BigQuery Connection**
5. Create new link to property **526836321**

---

## What to Do Once Linked

1. **Wait 24 hours** — GA4 exports data to BigQuery starting the next day
2. **Check BigQuery console** — Go to: https://console.cloud.google.com/bigquery
3. Look for table: `analytics_526836321.events_*`
4. If data appears, run: `python3 /Users/rreilly/.openclaw/workspace/scripts/bigquery_queries.py`

---

## If Still Stuck

Tell me:
- What you see in the **Data streams** section
- Any text that mentions "Cloud", "BigQuery", "Link", or "Export"
- Screenshot descriptions help!

Ready to try? Let me know what you find! 🍑
