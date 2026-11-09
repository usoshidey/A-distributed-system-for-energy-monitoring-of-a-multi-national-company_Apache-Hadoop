"""
Test Hadoop MapReduce and Hive Analytics Execution Pipeline.
"""

import os
from backend.services.hadoop_service import (
    is_hadoop_available,
    get_hadoop_status,
    execute_simulated_mapreduce,
    run_mapreduce_job
)
from backend.services.hive_service import execute_hive_analytics, get_hive_status


def test_hadoop_status_structure():
    status = get_hadoop_status()
    assert "installed" in status
    assert "active_engine" in status
    assert "hdfs_directories" in status
    assert "/energy-monitoring/raw-data" in status["hdfs_directories"]


def test_mapreduce_pipeline_execution():
    result = execute_simulated_mapreduce()
    assert "results" in result
    assert result["total_records_processed"] >= 10000

    results = result["results"]
    countries = [r["country"] for r in results]
    for c in ["India", "USA", "Germany", "Japan"]:
        assert c in countries

    for r in results:
        assert r["total_consumption_kwh"] > 0
        assert r["avg_consumption_kwh"] > 0
        assert r["record_count"] > 0


def test_mapreduce_job_trigger():
    res = run_mapreduce_job()
    assert "results" in res
    assert "job_id" in res


def test_hive_analytics_execution():
    analytics = execute_hive_analytics("all")
    assert "global_metrics" in analytics
    assert "country_wise" in analytics
    assert "branch_wise" in analytics
    assert "daily_trends" in analytics
    assert "monthly_trends" in analytics
    assert "expenditure" in analytics

    # Check that highest consuming branch is computed
    assert analytics["highest_consuming_branch"] is not None
    assert "branch_name" in analytics["highest_consuming_branch"]

