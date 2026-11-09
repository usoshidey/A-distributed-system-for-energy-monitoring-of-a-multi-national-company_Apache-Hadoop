/**
 * Report Generation and Export Script
 * Filters energy consumption records and generates downloadable CSV and JSON summaries.
 */

async function generateReport() {
    API.checkAuth();
    const country = document.getElementById("report-country").value;
    const branch = document.getElementById("report-branch").value;
    const startDate = document.getElementById("report-start-date").value;
    const endDate = document.getElementById("report-end-date").value;

    const queryParams = new URLSearchParams({
        country: country || "All",
        branch: branch || "All",
        start_date: startDate || "",
        end_date: endDate || "",
        limit: 150
    });

    try {
        const res = await API.get(`/reports?${queryParams.toString()}`);
        renderReportSummary(res.summary);
        renderReportTable(res.data);
    } catch (err) {
        API.showToast("Failed to generate report: " + err.message, "danger");
    }
}

function renderReportSummary(s) {
    if (!s) return;
    document.getElementById("summary-matched-count").textContent = API.formatNumber(s.total_records_matched, 0);
    document.getElementById("summary-total-kwh").textContent = `${API.formatNumber(s.total_consumption_kwh)} kWh`;
    document.getElementById("summary-avg-kwh").textContent = `${API.formatNumber(s.average_consumption_kwh)} kWh`;
    document.getElementById("summary-peak-kwh").textContent = `${API.formatNumber(s.max_consumption_kwh)} kWh`;
    document.getElementById("report-summary-card").style.display = "block";
}

function renderReportTable(rows) {
    const tbody = document.getElementById("table-report-body");
    if (!tbody) return;

    if (!rows || rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No telemetry records match the specified filters.</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map(r => `
        <tr>
            <td><span class="badge bg-light text-dark border font-monospace">${r.reading_id}</span></td>
            <td><strong>${r.branch_name}</strong></td>
            <td>${r.country}</td>
            <td><strong class="text-primary">${API.formatNumber(r.energy_kwh)}</strong> kWh</td>
            <td>${r.voltage} V</td>
            <td>${r.current} A</td>
            <td class="text-muted small">${r.timestamp}</td>
        </tr>
    `).join("");
}

function exportCSV() {
    const country = document.getElementById("report-country").value;
    const branch = document.getElementById("report-branch").value;
    const startDate = document.getElementById("report-start-date").value;
    const endDate = document.getElementById("report-end-date").value;

    const queryParams = new URLSearchParams({
        country: country || "All",
        branch: branch || "All",
        start_date: startDate || "",
        end_date: endDate || ""
    });

    window.location.href = `/api/reports/export?${queryParams.toString()}`;
    API.showToast("Preparing CSV export download...", "info");
}

async function downloadSummary() {
    const country = document.getElementById("report-country").value;
    const branch = document.getElementById("report-branch").value;
    const startDate = document.getElementById("report-start-date").value;
    const endDate = document.getElementById("report-end-date").value;

    const queryParams = new URLSearchParams({
        country: country || "All",
        branch: branch || "All",
        start_date: startDate || "",
        end_date: endDate || ""
    });

    try {
        const res = await API.get(`/reports/summary?${queryParams.toString()}`);
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(res, null, 2));
        const dlAnchor = document.createElement("a");
        dlAnchor.setAttribute("href", dataStr);
        dlAnchor.setAttribute("download", `energy_summary_${country || 'global'}.json`);
        document.body.appendChild(dlAnchor);
        dlAnchor.click();
        dlAnchor.remove();
        API.showToast("Summary report JSON downloaded.", "success");
    } catch (err) {
        API.showToast("Failed to download summary.", "danger");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    generateReport();
    document.getElementById("btn-generate-report")?.addEventListener("click", generateReport);
    document.getElementById("btn-export-csv")?.addEventListener("click", exportCSV);
    document.getElementById("btn-download-summary")?.addEventListener("click", downloadSummary);
});

