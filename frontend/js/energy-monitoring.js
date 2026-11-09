/**
 * Energy Monitoring Script
 * Real-time meter telemetry feed and ingestion form with automated anomaly detection.
 */

let currentOffset = 0;
const pageSize = 50;

async function loadReadings(reset = false) {
    API.checkAuth();
    if (reset) currentOffset = 0;

    const country = document.getElementById("filter-country")?.value || "";
    const branch = document.getElementById("filter-branch")?.value || "";

    const url = `/energy/readings?limit=${pageSize}&offset=${currentOffset}&country=${encodeURIComponent(country)}&branch=${encodeURIComponent(branch)}`;

    try {
        const res = await API.get(url);
        const tbody = document.getElementById("table-telemetry-body");
        if (!tbody) return;

        document.getElementById("telemetry-count").textContent = `Showing ${currentOffset + 1} - ${Math.min(currentOffset + pageSize, res.total)} of ${API.formatNumber(res.total, 0)} records`;

        tbody.innerHTML = res.readings.map(r => `
            <tr>
                <td><span class="badge bg-light text-dark border font-monospace">${r.reading_id}</span></td>
                <td><span class="badge bg-secondary-subtle text-secondary font-monospace">${r.meter_code}</span></td>
                <td><strong>${r.branch_name}</strong></td>
                <td>${r.country}</td>
                <td class="text-muted small">${r.timestamp}</td>
                <td><strong class="text-primary">${API.formatNumber(r.energy_kwh)}</strong></td>
                <td>${r.voltage} V</td>
                <td>${r.current} A</td>
                <td>${r.power_factor}</td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Error loading readings:", err);
    }
}

function prevPage() {
    if (currentOffset >= pageSize) {
        currentOffset -= pageSize;
        loadReadings();
    }
}

function nextPage() {
    currentOffset += pageSize;
    loadReadings();
}

async function submitReading(e) {
    e.preventDefault();
    const branchName = document.getElementById("modal-branch-name").value;
    const meterCode = document.getElementById("modal-meter-code").value;
    const energyKwh = parseFloat(document.getElementById("modal-energy-kwh").value);
    const voltage = parseFloat(document.getElementById("modal-voltage").value) || 230;
    const powerFactor = parseFloat(document.getElementById("modal-power-factor").value) || 0.92;

    if (!branchName || !meterCode || isNaN(energyKwh)) {
        alert("Please complete required fields: Branch, Meter ID, and Energy Consumption.");
        return;
    }

    try {
        const payload = {
            branch_name: branchName,
            meter_code: meterCode,
            energy_kwh: energyKwh,
            voltage: voltage,
            power_factor: powerFactor
        };

        const res = await API.post("/energy/readings", payload);
        if (res.success) {
            // Close modal
            const modalEl = document.getElementById("addReadingModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            document.getElementById("form-add-reading").reset();

            if (res.anomaly_detected) {
                API.showToast(`🚨 ABNORMAL CONSUMPTION DETECTED! Reading exceeded 1.5x branch average (${res.alert.severity} alert created)`, "warning");
            } else {
                API.showToast("Energy reading logged and verified normal.", "success");
            }

            loadReadings(true);
        }
    } catch (err) {
        alert("Error saving reading: " + err.message);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadReadings();
    const form = document.getElementById("form-add-reading");
    if (form) form.addEventListener("submit", submitReading);

    document.getElementById("filter-country")?.addEventListener("change", () => loadReadings(true));
    document.getElementById("filter-branch")?.addEventListener("change", () => loadReadings(true));
});

