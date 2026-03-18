#!/bin/bash

#######################################
# GA4 to BigQuery Link Setup
# For ReillyDesignStudio Analytics
#######################################

PROJECT_ID="127601657025"
PROPERTY_ID="526836321"
DATASET="ga4_reillydesignstudio"
LOCATION="US"

echo "================================================"
echo "GA4 → BigQuery Link Setup"
echo "================================================"
echo ""
echo "Project ID:    $PROJECT_ID"
echo "Property ID:   $PROPERTY_ID"
echo "Dataset:       $DATASET"
echo "Location:      $LOCATION"
echo ""

# Step 1: Verify BigQuery dataset exists
echo "Step 1: Checking BigQuery dataset..."
DATASET_EXISTS=$(bq --project_id=$PROJECT_ID ls --dataset_id=$DATASET 2>&1 | grep -q $DATASET && echo "1" || echo "0")

if [ "$DATASET_EXISTS" = "1" ]; then
  echo "✓ Dataset '$DATASET' exists"
else
  echo "✗ Dataset not found. Creating..."
  bq --project_id=$PROJECT_ID mk --dataset --location=$LOCATION $DATASET
  echo "✓ Dataset created"
fi

# Step 2: Check if BigQuery Link exists in GA4
echo ""
echo "Step 2: Checking GA4 BigQuery links..."
echo "⚠️  NOTE: BigQuery linking must be done in Google Analytics Admin UI"
echo ""
echo "To complete the link manually:"
echo "1. Go to: https://analytics.google.com"
echo "2. Admin (bottom left) → Property → BigQuery Links"
echo "3. Click 'Link BigQuery Project'"
echo "4. Select Project: $PROJECT_ID"
echo "5. Select Dataset: $DATASET"
echo "6. Authorize & Confirm"
echo ""

# Step 3: Wait and check for data
echo "Step 3: Checking for GA4 event data..."
echo ""
echo "This may take 24-48 hours after linking before data appears."
echo ""

# Try to query for recent events
echo "Attempting to query recent events (this will fail if link isn't complete)..."
bq --project_id=$PROJECT_ID query --use_legacy_sql=false \
  'SELECT COUNT(*) as event_count FROM `127601657025.ga4_reillydesignstudio.events_*` WHERE _TABLE_SUFFIX >= FORMAT_DATE("%Y%m%d", CURRENT_DATE()-1)' \
  2>&1 || echo "✓ Link not yet active - data will flow after manual admin setup"

echo ""
echo "================================================"
echo "Next Steps:"
echo "================================================"
echo "1. Complete the link in Google Analytics Admin UI (see above)"
echo "2. Wait 24-48 hours for data to start streaming"
echo "3. Run this script again to verify: $0"
echo "4. Query data with: bq query --use_legacy_sql=false"
echo "   'SELECT * FROM \`$PROJECT_ID.$DATASET.events_*\` LIMIT 10'"
echo ""
