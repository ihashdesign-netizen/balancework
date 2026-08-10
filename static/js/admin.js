const BalanceAdmin = (() => {
  const API_BASE = window.BALANCEWORK_API || "";
  const TOKEN_KEY = "bts_admin_token";
  let currentTab = "devis_requests";

  const STATUS_OPTIONS = {
    devis_requests: ["nouveau", "en_cours", "traite", "annule"],
    appointments: ["confirme", "en_attente", "annule"],
    messages: ["nouveau", "traite", "annule"],
    payments: ["en_attente", "partiel", "paye", "retard", "annule"],
    service_followups: ["en_attente", "en_cours", "termine", "cloture", "annule"],
    client_service_suivis: {
      statut_paiement: ["en_attente", "paye", "retard"],
      statut_service: ["en_cours", "valide", "cloture"],
    },
  };

  function token() {
    return sessionStorage.getItem(TOKEN_KEY) || "";
  }

  async function api(path, options = {}) {
    const res = await fetch(API_BASE + path, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
        ...(options.headers || {}),
      },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Erreur");
    return data;
  }

  function login() {
    const input = document.getElementById("token-input");
    const err = document.getElementById("login-error");
    sessionStorage.setItem(TOKEN_KEY, input.value.trim());
    api("/api/admin/devis_requests")
      .then(() => {
        err.className = "alert";
        showPanel();
      })
      .catch(() => {
        sessionStorage.removeItem(TOKEN_KEY);
        err.className = "alert show alert-error";
        err.textContent = "Jeton invalide.";
      });
  }

  function logout() {
    sessionStorage.removeItem(TOKEN_KEY);
    document.getElementById("admin-panel").style.display = "none";
    document.getElementById("login-box").style.display = "";
  }

  function showPanel() {
    document.getElementById("login-box").style.display = "none";
    document.getElementById("admin-panel").style.display = "";
    loadTab(currentTab);
  }

  function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll(".admin-tabs button").forEach((b) => {
      b.classList.toggle("active", b.dataset.tab === tab);
    });
    loadTab(tab);
  }

  const COLUMNS = {
    devis_requests: [
      { key: "id", label: "N°" },
      { key: "name", label: "Nom" },
      { key: "email", label: "E-mail" },
      { key: "phone", label: "Tél." },
      { key: "company", label: "Société" },
      { key: "service_title", label: "Service" },
      { key: "budget", label: "Budget" },
      { key: "details", label: "Détails" },
      { key: "status", label: "Statut" },
      { key: "created_at", label: "Reçu le" },
    ],
    appointments: [
      { key: "id", label: "N°" },
      { key: "name", label: "Nom" },
      { key: "email", label: "E-mail" },
      { key: "phone", label: "Tél." },
      { key: "service_title", label: "Service" },
      { key: "date", label: "Date" },
      { key: "time", label: "Heure" },
      { key: "notes", label: "Notes" },
      { key: "status", label: "Statut" },
    ],
    messages: [
      { key: "id", label: "N°" },
      { key: "name", label: "Nom" },
      { key: "email", label: "E-mail" },
      { key: "phone", label: "Tél." },
      { key: "subject", label: "Sujet" },
      { key: "message", label: "Message" },
      { key: "status", label: "Statut" },
    ],
    clients: [
      { key: "id", label: "N°" },
      { key: "name", label: "Nom" },
      { key: "email", label: "E-mail" },
      { key: "phone", label: "Tél." },
      { key: "company", label: "Société" },
      { key: "notes", label: "Notes" },
      { key: "created_at", label: "Ajouté le" },
    ],
    payments: [
      { key: "id", label: "N°" },
      { key: "client_name", label: "Client" },
      { key: "amount", label: "Montant (TND)" },
      { key: "date", label: "Date" },
      { key: "status", label: "Statut" },
      { key: "method", label: "Mode" },
      { key: "notes", label: "Notes" },
    ],
    service_followups: [
      { key: "id", label: "N°" },
      { key: "client_name", label: "Client" },
      { key: "service_title", label: "Service" },
      { key: "status", label: "Statut" },
      { key: "start_date", label: "Début" },
      { key: "due_date", label: "Échéance" },
      { key: "notes", label: "Notes" },
    ],
    types_service: [
      { key: "id", label: "N°" },
      { key: "title", label: "Service" },
      { key: "slug", label: "Identifiant" },
      { key: "short_desc", label: "Résumé" },
    ],
    client_service_suivis: [
      { key: "id", label: "N°" },
      { key: "client_name", label: "Client" },
      { key: "service_title", label: "Service" },
      { key: "montant", label: "Montant (TND)" },
      { key: "statut_paiement", label: "Paiement" },
      { key: "statut_service", label: "Dossier" },
      { key: "date_echeance", label: "Échéance" },
      { key: "commentaire", label: "Notes" },
    ],
  };

  async function loadTab(tab) {
    const wrap = document.getElementById("tab-content");
    wrap.innerHTML = "<p>Chargement…</p>";
    try {
      const data = await api(`/api/admin/${tab}`);
      renderTable(tab, data.items || []);
    } catch (e) {
      wrap.innerHTML = `<div class="alert show alert-error">${e.message}</div>`;
    }
  }

  function renderTable(tab, items) {
    const wrap = document.getElementById("tab-content");
    if (!items.length) {
      wrap.innerHTML = '<p style="color:#64748b">Aucun élément pour le moment.</p>';
      return;
    }
    const cols = COLUMNS[tab];
    const head = cols.map((c) => `<th>${c.label}</th>`).join("");
    const body = items
      .map((item) => {
        const cells = cols
          .map((c) => {
            const value = item[c.key];
            if (c.key === "status" || c.key === "statut_paiement" || c.key === "statut_service") {
              const opts = Array.isArray(STATUS_OPTIONS[tab])
                ? STATUS_OPTIONS[tab]
                : (STATUS_OPTIONS[tab] || {})[c.key] || [];
              return `<td><select class="status-select" data-table="${tab}" data-field="${c.key}" data-id="${item.id}" onchange="BalanceAdmin.updateStatus(this)">
                ${opts.map((s) => `<option value="${s}" ${value === s ? "selected" : ""}>${s}</option>`).join("")}
              </select></td>`;
            }
            return `<td>${value == null || value === "" ? "—" : escapeHtml(String(value))}</td>`;
          })
          .join("");
        return `<tr>${cells}</tr>`;
      })
      .join("");
    wrap.innerHTML = `<table class="admin-table"><thead><tr>${head}<th></th></tr></thead><tbody>${body}</tbody></table>`;
  }

  async function updateStatus(select) {
    try {
      await api(`/api/admin/${select.dataset.table}`, {
        method: "PUT",
        body: JSON.stringify({
          id: Number(select.dataset.id),
          field: select.dataset.field || "status",
          status: select.value,
        }),
      });
    } catch (e) {
      alert(e.message);
      loadTab(currentTab);
    }
  }

  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (token()) {
      api("/api/admin/devis_requests")
        .then(showPanel)
        .catch(() => sessionStorage.removeItem(TOKEN_KEY));
    }
  });

  return { login, logout, switchTab, updateStatus };
})();
