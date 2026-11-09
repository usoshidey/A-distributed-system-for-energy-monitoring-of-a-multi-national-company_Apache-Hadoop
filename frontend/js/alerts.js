/**
 * Abnormal Consumption Alerts Management Script
 * Handles real-time anomaly monitoring, threshold filtering (>1.5x average), and administrative acknowledgment.
 */

async function loadAlerts() {
    API.checkAuth();
    const status = document.getElementById("filter-status")?.value || "";
    const severity = document.getElementById("filter-severity")?.value || "";
    const country = document.getElementById("filter-country")?.value || "";

    const url = `/alerts?status=${encodeURIComponent(status)}&severity=${encodeURIComponent(severity)}&country=${encodeURIComponent(country)}&limit=150`;

    try {
        const res = await API.get(url);
        document.getElementById("stat-pending").textContent = res.pending_count;
        document.getElementById("stat-acknowledged").textContent = res.acknowledged_count;
        document.getElementById("stat-total").textContent = res.total;

        const tbody = document.getElementById("table-alerts-body");
        if (!tbody) return;

        if (res.alerts.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted"><i class="bi bi-shield-check text-success fs-3 d-block mb-2"></i>No anomalies match selected filters.</td></tr>`;
            return;
        }

        tbody.innerHTML = res.alerts.map(a => {
            const sevBadge = a.severity === "Critical" ? "badge-sev-critical" :
                             (a.severity === "High" ? "badge-sev-high" : "badge-sev-warning");
            const statusBadge = a.status === "Acknowledged" ?
                `<span class="badge bg-success-subtle text-success">Acknowledged</span>` :
                `<span class="badge bg-danger-subtle text-danger">Pending</span>`;

            return `
                <tr>
                    <td><span class="badge bg-light text-dark border font-monospace">#${a.id}</span></td>
                    <td><strong>${a.branch_name}</strong></td>
                    <td>${a.country}</td>
                    <td><strong class="text-danger">${API.formatNumber(a.current_kwh)} kWh</strong></td>
                    <td>${API.formatNumber(a.average_kwh)} kWh</td>
                    <td><span class="${sevBadge}">${a.severity} (${a.ratio.toFixed(2)}x baseline)</span></td>
                    <td class="text-muted small">${a.timestamp}</td>
                    <td>
                        ${a.status === "Pending" ?
                            `<button class="btn btn-sm btn-primary py-1 px-3" onclick="handleAcknowledge(${a.id})">Acknowledge</button>` :
                            `<div class="small text-muted"><i class="bi bi-check-circle-fill text-success"></i> ${a.acknowledged_by || 'Admin'}<div class="text-muted" style="font-size:0.75rem">${a.acknowledged_at || ''}</div></div>`}
                    </td>
                </tr>
            `;
        }).join("");
    } catch (err) {
        console.error("Error loading alerts:", err);
    }
}

async function handleAcknowledge(alertId) {
    const user = API.getCurrentUser();
    const username = user ? user.username : "Admin";

    try {
        const res = await API.post("/alerts/acknowledge", {
            alert_id: alertId,
            acknowledged_by: username
        });
        if (res.success) {
            API.showToast(`Alert #${alertId} has been acknowledged.`, "success");
            loadAlerts();
        }
    } catch (err) {
        API.showToast("Failed to acknowledge alert: " + err.message, "danger");
    }
}

async function scanAnomalies() {
    try {
        API.showToast("Initiating baseline anomaly scan across all readings...", "info");
        const res = await API.post("/alerts/scan");
        if (res.success) {
            API.showToast(`Scan complete: ${res.result.scanned_readings} records scanned. ${res.result.new_alerts_created} new spikes found.`, "success");
            loadAlerts();
        }
    } catch (err) {
        API.showToast("Scan failed: " + err.message, "danger");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadAlerts();
    document.getElementById("filter-status")?.addEventListener("change", loadAlerts);
    document.getElementById("filter-severity")?.addEventListener("change", loadAlerts);
    document.getElementById("filter-country")?.addEventListener("change", loadAlerts);
    document.getElementById("btn-scan-anomalies")?.addEventListener("click", scanAnomalies);
});

