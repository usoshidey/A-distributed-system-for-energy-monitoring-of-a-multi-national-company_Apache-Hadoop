@echo off
REM Windows Batch HDFS Setup Script
echo === [1/3] Verifying HDFS Command ===
where hdfs >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 'hdfs' command not found in PATH.
    echo Please ensure Hadoop is installed and winutils configured on Windows.
    exit /b 1
)

echo === [2/3] Creating HDFS Directories ===
hdfs dfs -mkdir -p /energy-monitoring/raw-data
hdfs dfs -mkdir -p /energy-monitoring/processed-data
hdfs dfs -mkdir -p /energy-monitoring/reports

echo === [3/3] Uploading CSV Data to HDFS ===
hdfs dfs -put -f ..\data\energy_data.csv /energy-monitoring/raw-data/energy_data.csv
echo HDFS setup completed!

