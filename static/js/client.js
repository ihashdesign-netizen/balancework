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
      wrap.innerHTML = '<p style="color:#64748b">Aucun dossier en cours pour le moment. Ouvrez un dossier ci-dessus.</p>';
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

  let selectedService = null;

  async function renderServices() {
    const wrap = document.getElementById("services-list");
    try {
      const data = await api("/api/services");
      if (!(data.services || []).length) {
        wrap.innerHTML = '<p style="color:#64748b">Aucun service disponible.</p>';
        return;
      }
      wrap.innerHTML = data.services
        .map(
          (s) => `<div class="svc-row">
            <div>
              <strong>${s.title}</strong>
              <p>${s.short_desc}</p>
            </div>
            <button class="btn" onclick="BalanceClient.selectService(${s.id}, '${escapeHtml(s.title).replace(/'/g, "\\'")}')">Ouvrir dossier</button>
          </div>`,
        )
        .join("");
    } catch (e) {
      wrap.innerHTML = `<p style="color:#b91c1c">${e.message}</p>`;
    }
  }

  function selectService(id, title) {
    selectedService = id;
    document.getElementById("dos-service-label").textContent = `Service : ${title}`;
    document.getElementById("dossier-form").style.display = "";
    document.getElementById("dos-description").focus();
  }

  function cancelDossier() {
    selectedService = null;
    document.getElementById("dossier-form").style.display = "none";
    document.getElementById("dos-description").value = "";
  }

  async function openDossier() {
    const desc = document.getElementById("dos-description").value.trim();
    if (!selectedService || !desc) {
      showAlert("dashboard-alert", "error", "Choisissez un service et décrivez votre besoin.");
      return;
    }
    const btn = event.target;
    btn.disabled = true;
    try {
      const data = await api("/api/client/dossiers", {
        method: "POST",
        body: JSON.stringify({ type_service: selectedService, description: desc }),
      });
      showAlert("dashboard-alert", "success", data.message);
      cancelDossier();
      api("/api/client/dashboard")
        .then((d) => renderSuivis(d.suivis || []))
        .catch(() => {});
    } catch (err) {
      showAlert("dashboard-alert", "error", err.message);
    } finally {
      btn.disabled = false;
    }
  }

  async function loadMessages() {
    const wrap = document.getElementById("messages-thread");
    try {
      const data = await api("/api/client/messages");
      if (!(data.messages || []).length) {
        wrap.innerHTML = '<p style="color:#64748b">Aucun message pour le moment.</p>';
        return;
      }
      wrap.innerHTML = data.messages
        .map((m) => `<div class="msg ${m.direction === "admin" ? "msg-admin" : "msg-client"}"><strong>${m.direction === "admin" ? "Cabinet" : "Vous"}</strong> — <small>${m.created_at}</small><p>${escapeHtml(m.text)}</p></div>`)
        .join("");
      wrap.scrollTop = wrap.scrollHeight;
    } catch (e) {
      wrap.innerHTML = `<p style="color:#b91c1c">${e.message}</p>`;
    }
  }

  async function sendMessage() {
    const text = document.getElementById("msg-text").value.trim();
    if (!text) {
      showAlert("dashboard-alert", "error", "Écrivez un message.");
      return;
    }
    const btn = event.target;
    btn.disabled = true;
    try {
      await api("/api/client/messages", { method: "POST", body: JSON.stringify({ text }) });
      document.getElementById("msg-text").value = "";
      await loadMessages();
    } catch (err) {
      showAlert("dashboard-alert", "error", err.message);
    } finally {
      btn.disabled = false;
    }
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function showDashboard(client) {
    document.getElementById("auth-box").style.display = "none";
    document.getElementById("dashboard-box").style.display = "";
    document.getElementById("client-welcome").textContent =
      `Bienvenue ${client.name}${client.matricule_fiscale ? " — Matricule : " + client.matricule_fiscale : ""}`;
    renderServices();
    loadMessages();
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

  return { login, register, logout, openDossier, sendMessage, selectService, cancelDossier };
})();
