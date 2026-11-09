@echo off
REM Windows Hive Runner Script
echo === Checking Hive CLI ===
where hive >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 'hive' command not found.
    echo Use the web backend analytics interface to execute Hive SQL queries.
    exit /b 1
)

hive -f analytics_queries.hql

