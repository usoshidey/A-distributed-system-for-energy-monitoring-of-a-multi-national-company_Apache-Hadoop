#!/bin/bash
# ==============================================================================
# HDFS Directory Setup and Data Ingestion Script
# Distributed Energy Monitoring System
# ==============================================================================

set -e

echo "=== [1/4] Verifying Apache Hadoop Environment ==="
if ! command -v hdfs &> /dev/null; then
    echo "ERROR: 'hdfs' command not found. Please ensure HADOOP_HOME is set and on PATH."
    exit 1
fi

echo "Connected to Hadoop cluster: $(hadoop version | head -n 1)"

echo "=== [2/4] Creating HDFS Directory Hierarchy ==="
hdfs dfs -mkdir -p /energy-monitoring/raw-data
hdfs dfs -mkdir -p /energy-monitoring/processed-data
hdfs dfs -mkdir -p /energy-monitoring/reports

echo "Created directories:"
hdfs dfs -ls /energy-monitoring

echo "=== [3/4] Uploading Raw Energy Telemetry Data to HDFS ==="
DATA_FILE="../data/energy_data.csv"
if [ ! -f "$DATA_FILE" ]; then
    echo "Warning: $DATA_FILE not found in ../data. Generating sample dataset first..."
    python3 ../data/generate_data.py
fi

hdfs dfs -put -f "$DATA_FILE" /energy-monitoring/raw-data/energy_data.csv

echo "=== [4/4] Verifying File Placement on HDFS ==="
hdfs dfs -ls -h /energy-monitoring/raw-data/

echo "HDFS setup completed successfully!"

