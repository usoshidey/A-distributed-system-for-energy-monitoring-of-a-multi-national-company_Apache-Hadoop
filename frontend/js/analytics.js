/**
 * Big Data Analytics Console
 * Triggers Apache Hadoop MapReduce jobs and executes Apache Hive HQL analytical queries.
 */

async function initAnalytics() {
    API.checkAuth();
    loadJobHistory();
    loadHiveSummary();
}

async function runMapReduce() {
    const term = document.getElementById("terminal-output");
    term.innerHTML = `<span class="term-info">[INFO] Initializing MapReduce job submission...</span><br>`;
    term.innerHTML += `<span class="term-info">[INFO] Input Path: /energy-monitoring/raw-data/energy_data.csv</span><br>`;
    term.innerHTML += `<span class="term-info">[INFO] Target Output: /energy-monitoring/processed-data/country_summary</span><br>`;

    try {
        term.innerHTML += `<span class="term-cmd">> Configuring Mapper (EnergyMapper.java) & Reducer (EnergyReducer.java)...</span><br>`;
        term.innerHTML += `<span class="term-cmd">> Splitting input records & allocating tasks across data partitions...</span><br>`;
        
        const res = await API.post("/analytics/mapreduce/run");
        if (res.success) {
            const job = res.job;
            term.innerHTML += `<span class="term-info">> Execution Engine: ${job.engine}</span><br>`;
            term.innerHTML += `<span class="term-info">> Records Ingested: ${job.total_records_processed.toLocaleString()} records</span><br>`;
            term.innerHTML += `<span class="term-info">> Map Phase: Extracted Country Key & Consumption Value</span><br>`;
            term.innerHTML += `<span class="term-info">> Shuffle & Sort: Grouped telemetry by Country key partitions</span><br>`;
            term.innerHTML += `<span class="term-info">> Reduce Phase: Computed Total kWh, Average kWh, and record counts</span><br>`;
            term.innerHTML += `<span class="term-success">[SUCCESS] MapReduce Job Completed in ${job.duration_seconds}s!</span><br><br>`;
            term.innerHTML += `<span class="term-cmd">=== MapReduce Reduced Output Stream ===</span><br>`;

            job.results.forEach(r => {
                term.innerHTML += `Key: <strong class="text-white">${r.country.padEnd(10, ' ')}</strong> | Total: ${r.total_consumption_kwh.toLocaleString()} kWh | Avg: ${r.avg_consumption_kwh.toFixed(2)} kWh | Count: ${r.record_count}<br>`;
            });

            API.showToast("MapReduce Job completed successfully!", "success");
            loadJobHistory();
        }
    } catch (err) {
        term.innerHTML += `<span class="term-warn">[ERROR] Job execution failed: ${err.message}</span><br>`;
        API.showToast("MapReduce failed to execute.", "danger");
    }
}

async function runHiveQueries() {
    const term = document.getElementById("terminal-output");
    term.innerHTML = `<span class="term-info">[INFO] Connecting to Apache Hive / Beeline Service...</span><br>`;
    term.innerHTML += `<span class="term-info">[INFO] Database: energy_db | Table: raw_energy_readings</span><br>`;

    try {
        const res = await API.post("/analytics/hive/run");
        if (res.success) {
            const data = res.results;
            term.innerHTML += `<span class="term-info">> Active Engine: ${data.engine}</span><br>`;
            term.innerHTML += `<span class="term-cmd">> Executing Query 1: Global Consumption Aggregation</span><br>`;
            term.innerHTML += `  Total: ${data.global_metrics.total_consumption_kwh.toLocaleString()} kWh | Readings: ${data.global_metrics.total_readings.toLocaleString()}<br>`;
            term.innerHTML += `<span class="term-cmd">> Executing Query 2: Country-Wise Aggregation & Multi-Currency Expenditure</span><br>`;
            data.expenditure.forEach(e => {
                term.innerHTML += `  ${e.country}: ${e.total_kwh.toLocaleString()} kWh @ ${e.currency_symbol}${e.tariff_rate}/kWh -> Local: ${e.local_cost_formatted} | USD Eq: ${e.usd_formatted}<br>`;
            });
            term.innerHTML += `<span class="term-cmd">> Executing Query 6: Highest Consuming Branch Window Function (DENSE_RANK)</span><br>`;
            if (data.highest_consuming_branch) {
                term.innerHTML += `  Rank #1: ${data.highest_consuming_branch.branch_name} (${data.highest_consuming_branch.country}) - ${data.highest_consuming_branch.total_kwh.toLocaleString()} kWh<br>`;
            }
            term.innerHTML += `<span class="term-success">[SUCCESS] All Hive Analytical Queries executed successfully!</span><br>`;

            API.showToast("Hive Analytics executed successfully!", "success");
            renderHiveTables(data);
        }
    } catch (err) {
        term.innerHTML += `<span class="term-warn">[ERROR] Hive query execution failed: ${err.message}</span><br>`;
        API.showToast("Hive queries failed to execute.", "danger");
    }
}

async function loadHiveSummary() {
    try {
        const data = await API.get("/analytics/all");
        renderHiveTables(data);
    } catch (err) {
        console.error("Error loading analytics data:", err);
    }
}

function renderHiveTables(data) {
    if (!data) return;

    // Country summary
    const countryTbody = document.getElementById("hive-country-body");
    if (countryTbody && data.country_wise) {
        countryTbody.innerHTML = data.country_wise.map(c => `
            <tr>
                <td><strong>${c.country}</strong></td>
                <td><span class="badge bg-secondary-subtle text-secondary">${c.code}</span></td>
                <td>${API.formatNumber(c.records, 0)}</td>
                <td><strong class="text-primary">${API.formatNumber(c.total_kwh)}</strong> kWh</td>
                <td>${API.formatNumber(c.avg_kwh)} kWh</td>
                <td>${c.avg_voltage} V</td>
                <td>${c.avg_power_factor}</td>
            </tr>
        `).join("");
    }

    // Branch ranking
    const branchTbody = document.getElementById("hive-branch-body");
    if (branchTbody && data.branch_wise) {
        branchTbody.innerHTML = data.branch_wise.map((b, idx) => `
            <tr>
                <td><span class="badge ${idx === 0 ? 'bg-danger' : 'bg-light text-dark border'}">#${idx + 1}</span></td>
                <td><strong>${b.branch_name}</strong></td>
                <td><span class="badge ${b.branch_type === 'factory' ? 'badge-factory' : 'badge-office'}">${b.branch_type}</span></td>
                <td>${b.country}</td>
                <td><strong class="text-primary">${API.formatNumber(b.total_kwh)}</strong> kWh</td>
                <td>${API.formatNumber(b.avg_kwh)} kWh</td>
                <td><span class="text-danger fw-bold">${API.formatNumber(b.peak_kwh)} kWh</span></td>
            </tr>
        `).join("");
    }
}

async function loadJobHistory() {
    try {
        const res = await API.get("/analytics/jobs");
        const tbody = document.getElementById("job-history-body");
        if (!tbody) return;

        tbody.innerHTML = res.jobs.map(j => `
            <tr>
                <td><span class="badge bg-light text-dark border font-monospace">${j.job_id}</span></td>
                <td><span class="badge bg-primary-subtle text-primary">${j.job_type}</span></td>
                <td><span class="badge bg-success-subtle text-success">${j.status}</span></td>
                <td class="small text-muted">${j.execution_engine}</td>
                <td>${API.formatNumber(j.records_processed, 0)}</td>
                <td>${j.duration_seconds}s</td>
                <td class="small text-muted">${j.created_at}</td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Error loading job history:", err);
    }
}

document.addEventListener("DOMContentLoaded", initAnalytics);

