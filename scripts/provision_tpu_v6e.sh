#!/bin/bash
# Provision a TPU v6e-1 (Trillium) VM on Google Cloud
# Run this from your local machine with gcloud authenticated

set -e

# --- Config ---
PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project)}"
TPU_NAME="momo-akira-tpu"
ZONE="us-central2-b"        # v6e available zones: us-central2-b, us-east1-d
ACCELERATOR_TYPE="v6e-1"    # 1 chip, 16GB HBM2e
RUNTIME_VERSION="tpu-vm-tf-2.16.0-pjrt"  # PyTorch/XLA compatible runtime
MACHINE_TYPE="ct6e-standard-4t"  # v6e-1 standard machine type

echo "=== Provisioning TPU v6e-1 ==="
echo "Project:  $PROJECT_ID"
echo "TPU name: $TPU_NAME"
echo "Zone:     $ZONE"
echo "Type:     $ACCELERATOR_TYPE"
echo ""

# Create the TPU VM
gcloud compute tpus tpu-vm create "$TPU_NAME" \
  --project="$PROJECT_ID" \
  --zone="$ZONE" \
  --accelerator-type="$ACCELERATOR_TYPE" \
  --version="$RUNTIME_VERSION"

echo "✅ TPU VM created: $TPU_NAME"
echo ""
echo "=== Copying training files ==="

# Copy training script to TPU VM
gcloud compute tpus tpu-vm scp \
  ~/.openclaw/workspace/scripts/train_drafter_tpu_v6e.py \
  ~/.openclaw/workspace/scripts/setup_tpu_v6e.sh \
  "$TPU_NAME":~/ \
  --zone="$ZONE"

echo "✅ Files copied"
echo ""
echo "=== Running setup on TPU VM ==="

# Run setup
gcloud compute tpus tpu-vm ssh "$TPU_NAME" \
  --zone="$ZONE" \
  --command="bash ~/setup_tpu_v6e.sh"

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To start training:"
echo "  gcloud compute tpus tpu-vm ssh $TPU_NAME --zone=$ZONE \\"
echo "    --command='nohup python3 train_drafter_tpu_v6e.py > training.log 2>&1 &'"
echo ""
echo "To monitor:"
echo "  gcloud compute tpus tpu-vm ssh $TPU_NAME --zone=$ZONE \\"
echo "    --command='tail -f training.log'"
echo ""
echo "To download weights when done:"
echo "  gcloud compute tpus tpu-vm scp $TPU_NAME:~/drafter_output_tpu/ . \\"
echo "    --recurse --zone=$ZONE"
echo ""
echo "To delete VM when done (saves money):"
echo "  gcloud compute tpus tpu-vm delete $TPU_NAME --zone=$ZONE"
