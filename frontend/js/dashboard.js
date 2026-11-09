/**
 * Executive Energy Dashboard Script
 * Renders 5 Chart.js analytical charts, real-time KPIs, alert lists, and Hadoop cluster telemetry.
 */

let chartDaily = null;
let chartMonthly = null;
let chartCountry = null;
let chartBranch = null;
let chartPie = null;

async function initDashboard() {
    API.checkAuth();
    try {
        const data = await API.get("/dashboard");
        renderKPIs(data.kpi);
        renderCharts(data.charts);
        renderRecentReadings(data.recent_readings);
        renderRecentAlerts(data.recent_alerts);
        renderClusterStatus(data.bigdata_status);
        renderExpenditureTable(data.expenditure_breakdown);
    } catch (err) {
        console.error("Dashboard loading error:", err);
        API.showToast("Failed to load dashboard metrics. Retrying...", "danger");
    }
}

function renderKPIs(kpi) {
    if (!kpi) return;
    document.getElementById("kpi-global-kwh").textContent = `${API.formatNumber(kpi.total_consumption_kwh)} kWh`;
    document.getElementById("kpi-global-cost").textContent = `$ ${API.formatNumber(kpi.total_expenditure_usd)}`;
    document.getElementById("kpi-countries-count").textContent = kpi.total_countries;
    document.getElementById("kpi-branches-count").textContent = kpi.total_branches;
    document.getElementById("kpi-highest-country").textContent = kpi.highest_consuming_country;
    document.getElementById("kpi-highest-branch").textContent = kpi.highest_consuming_branch;
    
    const alertCountEl = document.getElementById("kpi-pending-alerts");
    if (alertCountEl) {
        alertCountEl.textContent = kpi.pending_alerts_count;
    }
}

function renderCharts(charts) {
    if (!charts) return;

    // Palette
    const blueGradient = "#2563eb";
    const tealColor = "#06b6d4";
    const amberColor = "#f59e0b";
    const violetColor = "#8b5cf6";

    // 1. Daily Consumption Trend (Line Chart)
    const ctxDaily = document.getElementById("chartDaily").getContext("2d");
    if (chartDaily) chartDaily.destroy();
    chartDaily = new Chart(ctxDaily, {
        type: "line",
        data: {
            labels: charts.daily.labels,
            datasets: [
                {
                    label: "Daily Total Consumption (kWh)",
                    data: charts.daily.values,
                    borderColor: blueGradient,
                    backgroundColor: "rgba(37, 99, 235, 0.08)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.35,
                    pointRadius: 2,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "top" },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.parsed.y.toLocaleString()} kWh`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: "#f1f5f9" },
                    title: { display: true, text: "Energy (kWh)" }
                },
                x: {
                    grid: { display: false },
                    ticks: { maxTicksLimit: 12 }
                }
            }
        }
    });

    // 2. Monthly Consumption (Bar Chart)
    const ctxMonthly = document.getElementById("chartMonthly").getContext("2d");
    if (chartMonthly) chartMonthly.destroy();
    chartMonthly = new Chart(ctxMonthly, {
        type: "bar",
        data: {
            labels: charts.monthly.labels,
            datasets: [
                {
                    label: "Monthly Total (kWh)",
                    data: charts.monthly.values,
                    backgroundColor: "#1e3a8a",
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.parsed.y.toLocaleString()} kWh`
                    }
                }
            },
            scales: {
                y: { grid: { color: "#f1f5f9" } },
                x: { grid: { display: false } }
            }
        }
    });

    // 3. Country-wise Comparison (Bar Chart)
    const ctxCountry = document.getElementById("chartCountry").getContext("2d");
    if (chartCountry) chartCountry.destroy();
    chartCountry = new Chart(ctxCountry, {
        type: "bar",
        data: {
            labels: charts.country.labels,
            datasets: [
                {
                    label: "Total Consumption (kWh)",
                    data: charts.country.values,
                    backgroundColor: ["#2563eb", "#06b6d4", "#10b981", "#f59e0b"],
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { grid: { color: "#f1f5f9" } },
                x: { grid: { display: false } }
            }
        }
    });

    // 4. Branch-wise Consumption (Horizontal Bar Chart)
    const ctxBranch = document.getElementById("chartBranch").getContext("2d");
    if (chartBranch) chartBranch.destroy();
    chartBranch = new Chart(ctxBranch, {
        type: "bar",
        data: {
            labels: charts.branch.labels,
            datasets: [
                {
                    label: "Consumption (kWh)",
                    data: charts.branch.values,
                    backgroundColor: charts.branch.types.map(t => t === "factory" ? "#f59e0b" : "#3b82f6"),
                    borderRadius: 5
                }
            ]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { grid: { color: "#f1f5f9" } },
                y: { grid: { display: false } }
            }
        }
    });

    // 5. Energy Consumption Distribution (Doughnut Chart)
    const ctxPie = document.getElementById("chartDistributionPie").getContext("2d");
    if (chartPie) chartPie.destroy();
    chartPie = new Chart(ctxPie, {
        type: "doughnut",
        data: {
            labels: charts.distribution_pie.labels,
            datasets: [
                {
                    data: charts.distribution_pie.values,
                    backgroundColor: ["#1e3a8a", "#2563eb", "#06b6d4", "#10b981"],
                    borderWidth: 2,
                    hoverOffset: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

function renderRecentReadings(readings) {
    const tbody = document.getElementById("table-recent-readings");
    if (!tbody) return;
    if (!readings || readings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-3">No readings recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = readings.map(r => `
        <tr>
            <td><span class="badge bg-light text-dark border font-monospace">${r.reading_id}</span></td>
            <td><strong>${r.branch_name}</strong></td>
            <td>${r.country}</td>
            <td><strong class="text-primary">${API.formatNumber(r.energy_kwh)}</strong> kWh</td>
            <td>${r.voltage} V</td>
            <td>${r.power_factor}</td>
            <td class="text-muted small">${r.timestamp}</td>
        </tr>
    `).join("");
}

function renderRecentAlerts(alerts) {
    const tbody = document.getElementById("table-recent-alerts");
    if (!tbody) return;
    if (!alerts || alerts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-success py-3"><i class="bi bi-shield-check me-1"></i> No abnormal consumption spikes detected.</td></tr>`;
        return;
    }

    tbody.innerHTML = alerts.map(a => {
        const sevClass = a.severity === "Critical" ? "badge-sev-critical" :
                         (a.severity === "High" ? "badge-sev-high" : "badge-sev-warning");
        const statusBadge = a.status === "Acknowledged" ?
            `<span class="badge bg-success-subtle text-success">Acknowledged</span>` :
            `<span class="badge bg-danger-subtle text-danger">Pending</span>`;

        return `
            <tr>
                <td><strong>${a.branch_name}</strong> <span class="text-muted small">(${a.country})</span></td>
                <td><span class="text-danger fw-bold">${API.formatNumber(a.current_kwh)} kWh</span></td>
                <td>${API.formatNumber(a.average_kwh)} kWh</td>
                <td><span class="${sevClass}">${a.severity} (+${Math.round((a.ratio - 1) * 100)}%)</span></td>
                <td>${statusBadge}</td>
                <td>
                    ${a.status === "Pending" ?
                        `<button class="btn btn-sm btn-outline-primary py-0 px-2" onclick="acknowledgeAlert(${a.id})">Acknowledge</button>` :
                        `<span class="small text-muted">${a.acknowledged_by || 'Admin'}</span>`}
                </td>
            </tr>
        `;
    }).join("");
}

async function acknowledgeAlert(alertId) {
    try {
        const res = await API.post("/alerts/acknowledge", { alert_id: alertId });
        if (res.success) {
            API.showToast(`Alert #${alertId} acknowledged.`, "success");
            initDashboard();
        }
    } catch (err) {
        API.showToast("Failed to acknowledge alert.", "danger");
    }
}

function renderClusterStatus(status) {
    const badgeEl = document.getElementById("badge-cluster-status");
    if (!badgeEl || !status) return;

    if (status.hadoop && status.hadoop.installed && status.hadoop.cluster_connected) {
        badgeEl.className = "cluster-pill online";
        badgeEl.innerHTML = `<i class="bi bi-circle-fill text-success" style="font-size:0.55rem"></i> Hadoop Cluster Online (YARN + HDFS)`;
    } else {
        badgeEl.className = "cluster-pill fallback";
        badgeEl.innerHTML = `<i class="bi bi-cpu text-primary"></i> Standalone MapReduce Engine (Simulated)`;
    }
}

function renderExpenditureTable(breakdown) {
    const tbody = document.getElementById("table-expenditure-breakdown");
    if (!tbody || !breakdown) return;

    tbody.innerHTML = breakdown.map(c => `
        <tr>
            <td><strong>${c.country}</strong></td>
            <td>${API.formatNumber(c.energy_kwh)} kWh</td>
            <td>${c.currency_symbol} ${API.formatNumber(c.tariff_rate)} / kWh <span class="badge bg-light text-muted border">illustrative</span></td>
            <td><strong class="text-primary">${c.local_cost_formatted}</strong></td>
            <td><strong class="text-dark">${c.usd_formatted}</strong></td>
        </tr>
    `).join("");
}

document.addEventListener("DOMContentLoaded", initDashboard);

