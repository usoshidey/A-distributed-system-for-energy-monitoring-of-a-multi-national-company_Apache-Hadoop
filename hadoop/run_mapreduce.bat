@echo off
REM Windows Batch MapReduce Runner Script
echo === Checking Hadoop environment ===
where hadoop >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 'hadoop' command not found in PATH.
    exit /b 1
)

set INPUT_HDFS=/energy-monitoring/raw-data/energy_data.csv
set OUTPUT_HDFS=/energy-monitoring/processed-data/country_summary

echo === Removing previous output ===
hdfs dfs -rm -r -f %OUTPUT_HDFS%

echo === Running Hadoop Streaming with Python Mapper and Reducer ===
hadoop jar %HADOOP_HOME%\share\hadoop\tools\lib\hadoop-streaming*.jar ^
  -input %INPUT_HDFS% ^
  -output %OUTPUT_HDFS% ^
  -mapper "python mapper.py" ^
  -reducer "python reducer.py"

echo === Output from HDFS ===
hdfs dfs -cat %OUTPUT_HDFS%/part-00000

