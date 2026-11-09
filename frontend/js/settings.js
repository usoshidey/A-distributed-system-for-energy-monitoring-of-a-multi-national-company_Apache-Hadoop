/**
 * System Settings & Cluster Diagnostics Script
 * Manages electricity tariff rates and checks Big Data infrastructure topology.
 */

async function loadSettings() {
    API.checkAuth();
    loadTariffs();
    loadClusterDiagnostics();
}

async function loadTariffs() {
    try {
        const res = await API.get("/settings/tariffs");
        const tbody = document.getElementById("table-tariffs-body");
        if (!tbody) return;

        tbody.innerHTML = res.tariffs.map(t => `
            <tr>
                <td><strong>${t.country_name}</strong></td>
                <td><span class="badge bg-secondary-subtle text-secondary">${t.currency_code} (${t.currency_symbol})</span></td>
                <td>
                    <div class="input-group input-group-sm" style="max-width: 180px;">
                        <span class="input-group-text">${t.currency_symbol}</span>
                        <input type="number" step="0.01" class="form-control" id="tariff-input-${t.country_name}" value="${t.tariff_rate}">
                        <span class="input-group-text">/ kWh</span>
                    </div>
                </td>
                <td class="text-muted small">${t.effective_date}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="updateTariff('${t.country_name}')">
                        Update
                    </button>
                </td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Error loading tariffs:", err);
    }
}

async function updateTariff(countryName) {
    const inputEl = document.getElementById(`tariff-input-${countryName}`);
    if (!inputEl) return;
    const newRate = parseFloat(inputEl.value);

    if (isNaN(newRate) || newRate < 0) {
        alert("Please enter a valid non-negative tariff rate.");
        return;
    }

    try {
        const res = await API.post("/settings/tariffs", {
            country_name: countryName,
            tariff_rate: newRate
        });
        if (res.success) {
            API.showToast(res.message, "success");
            loadTariffs();
        }
    } catch (err) {
        API.showToast("Failed to update tariff: " + err.message, "danger");
    }
}

async function loadClusterDiagnostics() {
    try {
        const res = await API.get("/settings/hadoop-status");
        
        // Hadoop status badge
        const hadoopStatusEl = document.getElementById("diag-hadoop-status");
        if (hadoopStatusEl) {
            if (res.hadoop.installed && res.hadoop.cluster_connected) {
                hadoopStatusEl.innerHTML = `<span class="badge bg-success"><i class="bi bi-check-circle"></i> Connected to YARN & HDFS</span>`;
            } else {
                hadoopStatusEl.innerHTML = `<span class="badge bg-primary"><i class="bi bi-cpu"></i> Python MapReduce Standalone Engine Active</span>`;
            }
        }

        // Hive status badge
        const hiveStatusEl = document.getElementById("diag-hive-status");
        if (hiveStatusEl) {
            if (res.hive.installed) {
                hiveStatusEl.innerHTML = `<span class="badge bg-success"><i class="bi bi-check-circle"></i> Connected (${res.hive.active_engine})</span>`;
            } else {
                hiveStatusEl.innerHTML = `<span class="badge bg-info text-dark"><i class="bi bi-database"></i> Hive Simulation Engine Active</span>`;
            }
        }

        // HDFS paths
        const hdfsListEl = document.getElementById("diag-hdfs-dirs");
        if (hdfsListEl && res.hadoop.hdfs_directories) {
            hdfsListEl.innerHTML = res.hadoop.hdfs_directories.map(d => `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <code>${d}</code>
                    <span class="badge bg-light text-dark border">HDFS Path</span>
                </li>
            `).join("");
        }
    } catch (err) {
        console.error("Error loading diagnostics:", err);
    }
}

document.addEventListener("DOMContentLoaded", loadSettings);

