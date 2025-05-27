# ==============================================================================
# Script: collect.sh
# Description:
#   This script queries an API every minute for 3 minutes to retrieve sales data
#   for the following graphics card models:
#     - rtx3060
#     - rtx3070
#     - rtx3080
#     - rtx3090
#     - rx6700
#
#   The collected data is appended to a copy of the file:
#     data/raw/sales_data.csv
#
#   The output file is saved in the format:
#     data/raw/sales_YYYYMMDD_HHMM.csv
#   with the following columns:
#     timestamp, model, sales
#
#   Collection activity (requests, queried models, results, errors)
#   is recorded in a log file:
#     logs/collect.logs
#
#   The log should be human-readable and must include:
#     - The date and time of each request
#     - The queried models
#     - The retrieved sales data
#     - Any possible errors
# ==============================================================================

#! /bin/bash

GPUS=("rtx3060" "rtx3070" "rtx3080" "rtx3090" "rx6700")

DATA_DIR="data/raw"

FULL_DATA_FILE="data/raw/sales_data.csv"
OUTPUT_FILE="$DATA_DIR/sales_$(date -u +'%Y%m%d_%H%M').csv"
echo "timestamp,model,sales" > "$OUTPUT_FILE"

log() {
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] $1" >> "logs/collect.logs"
}

log "Starting collection for GPUs: ${GPUS[*]}"

for GPU in "${GPUS[@]}"; do
    log "Querying $GPU"
    SALES=$(curl -s "http://0.0.0.0:5000/$GPU")
    TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    echo "$TIMESTAMP,$GPU,$SALES" >> "$FULL_DATA_FILE"
    echo "$TIMESTAMP,$GPU,$SALES" >> "$OUTPUT_FILE"
    log "Retrieved $GPU: $SALES"
done

log "Data added to $FULL_DATA_FILE"
log "Output saved to $OUTPUT_FILE"
