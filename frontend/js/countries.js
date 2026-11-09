/**
 * Countries View Script
 * Displays country cards, active tariffs, branches, total consumption, and local currency billing.
 */

async function loadCountries() {
    API.checkAuth();
    try {
        const res = await API.get("/countries");
        const container = document.getElementById("countries-container");
        if (!container) return;

        const flags = {
            "India": "🇮🇳",
            "USA": "🇺🇸",
            "Germany": "🇩🇪",
            "Japan": "🇯🇵"
        };

        container.innerHTML = res.countries.map(c => `
            <div class="col-md-6 col-xl-3 mb-4">
                <div class="card h-100 shadow-sm border-0">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="card-title fw-bold m-0">${flags[c.name] || '🌐'} ${c.name}</h5>
                            <span class="badge bg-primary-subtle text-primary fw-bold">${c.code}</span>
                        </div>
                        <div class="mb-2">
                            <span class="text-muted small">Branches Monitored:</span>
                            <span class="float-end fw-bold">${c.branch_count}</span>
                        </div>
                        <div class="mb-2">
                            <span class="text-muted small">Total Readings:</span>
                            <span class="float-end fw-bold">${API.formatNumber(c.total_readings, 0)}</span>
                        </div>
                        <div class="mb-2">
                            <span class="text-muted small">Energy Consumed:</span>
                            <span class="float-end fw-bold text-primary">${API.formatNumber(c.total_kwh)} kWh</span>
                        </div>
                        <div class="mb-2">
                            <span class="text-muted small">Active Tariff:</span>
                            <span class="float-end">${c.currency_symbol} ${API.formatNumber(c.tariff_rate)} / kWh</span>
                        </div>
                        <hr class="my-2">
                        <div class="mb-1">
                            <span class="text-muted small">Local Cost:</span>
                            <div class="fw-bold text-success fs-5">${c.local_expenditure_formatted}</div>
                        </div>
                        <div class="text-muted small">
                            USD Equivalent: <strong>${c.usd_formatted}</strong>
                        </div>
                        <div class="mt-3">
                            <h6 class="small fw-bold text-muted mb-1">Company Branches:</h6>
                            <ul class="list-unstyled small mb-0">
                                ${(c.branches || []).map(b => `
                                    <li class="py-1 border-bottom d-flex justify-content-between">
                                        <span>${b.name}</span>
                                        <span class="badge ${b.branch_type === 'factory' ? 'badge-factory' : 'badge-office'}">${b.branch_type}</span>
                                    </li>
                                `).join("")}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `).join("");
    } catch (err) {
        console.error("Error loading countries:", err);
        API.showToast("Could not load country data.", "danger");
    }
}

document.addEventListener("DOMContentLoaded", loadCountries);

