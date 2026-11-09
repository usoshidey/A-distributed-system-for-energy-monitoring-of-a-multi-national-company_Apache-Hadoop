/**
 * Branches View Script
 * Manages branch directory, active IoT smart meters, and consumption baselines.
 */

async function loadBranches() {
    API.checkAuth();
    try {
        const res = await API.get("/branches");
        const tbody = document.getElementById("table-branches-body");
        if (!tbody) return;

        tbody.innerHTML = res.branches.map(b => `
            <tr>
                <td>
                    <strong>${b.name}</strong>
                    <div class="text-muted small">${b.city}, ${b.country}</div>
                </td>
                <td>
                    <span class="badge ${b.branch_type === 'factory' ? 'badge-factory' : 'badge-office'} text-uppercase">
                        ${b.branch_type}
                    </span>
                </td>
                <td>
                    <span class="fw-bold">${b.country}</span>
                </td>
                <td>
                    <div class="small">
                        ${(b.meters || []).map(m => `
                            <span class="badge bg-light text-dark border me-1 mb-1 font-monospace">${m.meter_code}</span>
                        `).join("")}
                    </div>
                </td>
                <td>
                    <strong class="text-primary">${API.formatNumber(b.total_kwh)}</strong> kWh
                    <div class="text-muted small">${API.formatNumber(b.readings_count, 0)} telemetry records</div>
                </td>
                <td>
                    ${API.formatNumber(b.avg_kwh)} kWh
                </td>
                <td>
                    <span class="text-danger fw-bold">${API.formatNumber(b.peak_kwh)} kWh</span>
                </td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Error loading branches:", err);
        API.showToast("Could not load branch information.", "danger");
    }
}

document.addEventListener("DOMContentLoaded", loadBranches);

