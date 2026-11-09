#!/bin/bash
# ==============================================================================
# Hive Execution Script
# Executes Hive table initialization and runs analytics queries via Beeline or Hive CLI.
# ==============================================================================

set -e

echo "=== [1/2] Checking Hive CLI Availability ==="
if ! command -v hive &> /dev/null && ! command -v beeline &> /dev/null; then
    echo "ERROR: Hive or Beeline CLI not detected on system PATH."
    echo "Use the application's integrated Hive query analytics engine to run these queries."
    exit 1
fi

echo "=== [2/2] Executing Hive Analytical Queries ==="
if command -v beeline &> /dev/null; then
    echo "Executing via Apache Beeline..."
    beeline -u "jdbc:hive2://localhost:10000/default" -f ./analytics_queries.hql
else
    echo "Executing via Hive CLI..."
    hive -f ./analytics_queries.hql
fi

echo "Hive analytics queries completed successfully!"

