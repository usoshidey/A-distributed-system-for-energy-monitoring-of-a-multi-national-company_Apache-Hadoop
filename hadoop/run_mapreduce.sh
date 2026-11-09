#!/bin/bash
# ==============================================================================
# MapReduce Compilation and Execution Script
# Compiles Java MapReduce classes, creates JAR, and submits Job to YARN.
# ==============================================================================

set -e

INPUT_HDFS="/energy-monitoring/raw-data/energy_data.csv"
OUTPUT_HDFS="/energy-monitoring/processed-data/country_summary"
BUILD_DIR="./build"
JAR_NAME="energy-monitoring-mr.jar"

echo "=== [1/5] Checking Apache Hadoop Environment ==="
if ! command -v hadoop &> /dev/null; then
    echo "ERROR: 'hadoop' command not found."
    echo "If running without Hadoop daemon, use the web interface or fallback Python MapReduce runner."
    exit 1
fi

echo "=== [2/5] Compiling Java MapReduce Sources ==="
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

javac -classpath $(hadoop classpath) -d "$BUILD_DIR" EnergyMapper.java EnergyReducer.java EnergyDriver.java

echo "=== [3/5] Packaging Compiled Classes into JAR ==="
jar -cvf "$JAR_NAME" -C "$BUILD_DIR" .

echo "=== [4/5] Submitting MapReduce Job to Hadoop Cluster ==="
hdfs dfs -rm -r -f "$OUTPUT_HDFS" || true

hadoop jar "$JAR_NAME" org.apache.hadoop.energymonitoring.EnergyDriver "$INPUT_HDFS" "$OUTPUT_HDFS"

echo "=== [5/5] MapReduce Job Output from HDFS ==="
hdfs dfs -cat "$OUTPUT_HDFS/part-r-00000"

echo ""
echo "MapReduce processing completed successfully!"

