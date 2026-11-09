/**
 * Central API Client and Application Helpers
 * Distributed Energy Monitoring System
 */

const API = {
    async get(endpoint) {
        try {
            const res = await fetch(`/api${endpoint}`, {
                headers: { "Content-Type": "application/json" }
            });
            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.error || `HTTP ${res.status}: ${res.statusText}`);
            }
            return await res.json();
        } catch (error) {
            console.error(`GET ${endpoint} error:`, error);
            throw error;
        }
    },

    async post(endpoint, data = {}) {
        try {
            const res = await fetch(`/api${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.error || `HTTP ${res.status}: ${res.statusText}`);
            }
            return await res.json();
        } catch (error) {
            console.error(`POST ${endpoint} error:`, error);
            throw error;
        }
    },

    // Session helpers
    getCurrentUser() {
        const u = localStorage.getItem("energy_user");
        if (u) {
            try { return JSON.parse(u); } catch (e) { return null; }
        }
        return null;
    },

    setCurrentUser(user) {
        localStorage.setItem("energy_user", JSON.stringify(user));
    },

    clearSession() {
        localStorage.removeItem("energy_user");
    },

    async logout() {
        try {
            await fetch("/api/auth/logout", { method: "POST" });
        } catch (e) {}
        this.clearSession();
        window.location.href = "login.html";
    },

    // Authentication Guard
    checkAuth(requiredRole = null) {
        const user = this.getCurrentUser();
        // If not logged in and not on login page, redirect
        if (!user && !window.location.pathname.endsWith("login.html") && !window.location.pathname.endsWith("login")) {
            window.location.href = "login.html";
            return null;
        }
        if (requiredRole && user && user.role !== requiredRole && user.role !== "admin") {
            alert("Access restricted: Admin privilege required.");
            window.location.href = "dashboard.html";
            return null;
        }
        return user;
    },

    // Formatters
    formatNumber(num, decimals = 2) {
        if (num === null || num === undefined || isNaN(num)) return "0.00";
        return Number(num).toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },

    formatCurrency(val, symbol = "$") {
        return `${symbol} ${this.formatNumber(val)}`;
    },

    showToast(message, type = "success") {
        let toastContainer = document.getElementById("toast-container");
        if (!toastContainer) {
            toastContainer = document.createElement("div");
            toastContainer.id = "toast-container";
            toastContainer.className = "toast-container position-fixed bottom-0 end-0 p-3";
            toastContainer.style.zIndex = "9999";
            document.body.appendChild(toastContainer);
        }

        const toastEl = document.createElement("div");
        const bgClass = type === "success" ? "bg-success" : (type === "warning" ? "bg-warning" : "bg-danger");
        toastEl.className = `toast align-items-center text-white ${bgClass} border-0 show`;
        toastEl.setAttribute("role", "alert");
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${message}</strong>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        toastContainer.appendChild(toastEl);
        setTimeout(() => toastEl.remove(), 4000);
    }
};

// UI Initialization Helper
document.addEventListener("DOMContentLoaded", () => {
    // Populate user profile info in navbar if present
    const user = API.getCurrentUser();
    const userBadge = document.getElementById("nav-user-name");
    const roleBadge = document.getElementById("nav-user-role");
    if (userBadge && user) {
        userBadge.textContent = user.full_name || user.username;
    }
    if (roleBadge && user) {
        roleBadge.textContent = user.role === "admin" ? "Global Admin" : `Mgr (${user.assigned_country || 'Regional'})`;
    }

    // Toggle mobile sidebar
    const toggleBtn = document.getElementById("sidebarToggle");
    const sidebar = document.querySelector(".sidebar");
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }
});

