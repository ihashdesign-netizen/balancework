const BalanceClient = (() => {
  const API_BASE = window.BALANCEWORK_API || "";
  const TOKEN_KEY = "bts_client_token";

  function token() {
    return localStorage.getItem(TOKEN_KEY) || "";
  }

  function showAlert(id, type, message) {
    const el = document.getElementById(id);
    el.className = `alert show alert-${type}`;
    el.textContent = message;
  }

  function clearAlert(id) {
    const el = document.getElementById(id);
    el.className = "alert";
    el.textContent = "";
  }

  async function api(path, options = {}) {
    const res = await fetch(API_BASE + path, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
        ...(options.headers || {}),
      },
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || "Erreur");
    return data;
  }

  async function login(e) {
    e.preventDefault();
    clearAlert("client-alert");
    const btn = e.target.querySelector("button");
    btn.disabled = true;
    try {
      const data = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: document.getElementById("login-email").value.trim(),
          password: document.getElementById("login-password").value,
        }),
      });
      localStorage.setItem(TOKEN_KEY, data.token);
      showDashboard(data.client);
    } catch (err) {
      showAlert("client-alert", "error", err.message);
    } finally {
      btn.disabled = false;
    }
  }

  async function register(e) {
    e.preventDefault();
    clearAlert("client-alert");
    const btn = e.target.querySelector("button");
    btn.disabled = true;
    try {
      const data = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          name: document.getElementById("reg-name").value.trim(),
          prenom: document.getElementById("reg-prenom").value.trim(),
          email: document.getElementById("reg-email").value.trim(),
          phone: document.getElementById("reg-phone").value.trim(),
          matricule_fiscale: document.getElementById("reg-matricule").value.trim(),
          cin: document.getElementById("reg-cin").value.trim(),
          password: document.getElementById("reg-password").value,
        }),
      });
      localStorage.setItem(TOKEN_KEY, data.token);
      showDashboard(data.client);
    } catch (err) {
      showAlert("client-alert", "error", err.message);
    } finally {
      btn.disabled = false;
    }
  }

  function logout() {
    api("/api/auth/logout", { method: "POST" }).catch(() => {});
    localStorage.removeItem(TOKEN_KEY);
    document.getElementById("dashboard-box").style.display = "none";
    document.getElementById("auth-box").style.display = "";
    clearAlert("client-alert");
  }

  function renderSuivis(suivis) {
    const wrap = document.getElementById("dashboard-content");
    if (!suivis.length) {
      wrap.innerHTML = '<p style="color:#64748b">Aucun dossier en cours pour le moment. Votre cabinet les ajoutera ici.</p>';
      return;
    }
    const rows = suivis
      .map((s) => {
        const badge = s.statut_service === "Clôturé" ? "badge confirme" : "badge nouveau";
        const pay = s.statut_paiement === "Payé" ? "badge confirme" : "badge nouveau";
        return `<tr>
          <td>${s.service}</td>
          <td>${s.date_echeance}</td>
          <td><span class="${badge}">${s.statut_service}</span></td>
          <td><span class="${pay}">${s.statut_paiement}</span></td>
          <td>${s.montant} TND</td>
          <td>${s.commentaire || "—"}</td>
        </tr>`;
      })
      .join("");
    wrap.innerHTML = `<table class="admin-table">
      <thead><tr><th>Service</th><th>Échéance</th><th>Statut dossier</th><th>Statut paiement</th><th>Montant</th><th>Notes</th></tr></thead>
      <tbody>${rows}</tbody></table>`;
  }

  function showDashboard(client) {
    document.getElementById("auth-box").style.display = "none";
    document.getElementById("dashboard-box").style.display = "";
    document.getElementById("client-welcome").textContent =
      `Bienvenue ${client.name}${client.matricule_fiscale ? " — Matricule : " + client.matricule_fiscale : ""}`;
    api("/api/client/dashboard")
      .then((data) => renderSuivis(data.suivis || []))
      .catch((err) => {
        document.getElementById("dashboard-content").innerHTML =
          `<div class="alert show alert-error">${err.message}</div>`;
      });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("login-form").addEventListener("submit", login);
    document.getElementById("register-form").addEventListener("submit", register);
    if (token()) {
      api("/api/client/dashboard")
        .then((data) => showDashboard(data.client))
        .catch(() => localStorage.removeItem(TOKEN_KEY));
    }
  });

  return { login, register, logout };
})();
