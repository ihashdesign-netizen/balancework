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
      frequence: ["ponctuel", "mensuel", "trimestriel", "semestriel", "annuel"],
    },
    dossier_tasks: { statut: ["a_faire", "en_cours", "termine"], repetition: ["ponctuel", "mensuel", "trimestriel", "semestriel", "annuel"] },
    prefactures: { statut: ["emise", "payee", "annulee"] },
    declarations: {
      statut: ["a_faire", "en_cours", "depose", "retard"],
      type_declaration: ["mensuelle", "acompte", "annuelle", "autre"],
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
    document.getElementById("create-box").style.display = "none";
    document.getElementById("create-box").innerHTML = "";
    document.getElementById("create-btn").style.display = CREATE_FORMS[tab] ? "" : "none";
    loadTab(tab);
  }

  const CREATE_FORMS = {
    clients: [
      { name: "name", label: "Nom *", type: "text" },
      { name: "prenom", label: "Prénom", type: "text" },
      { name: "email", label: "E-mail *", type: "email" },
      { name: "phone", label: "Téléphone", type: "text" },
      { name: "company", label: "Société", type: "text" },
      { name: "matricule_fiscale", label: "Matricule fiscale", type: "text" },
      { name: "cin", label: "CIN", type: "text" },
      { name: "notes", label: "Notes", type: "textarea" },
    ],
    client_service_suivis: [
      { name: "client", label: "Client *", type: "select", source: "/api/admin/clients", valueKey: "id", textKey: (c) => c.name },
      { name: "type_service", label: "Service *", type: "select", source: "/api/admin/types_service", valueKey: "id", textKey: (s) => s.title },
      { name: "montant", label: "Montant (TND) *", type: "number", step: "0.001" },
      { name: "statut_paiement", label: "Statut paiement", type: "select", options: ["en_attente", "paye", "retard"] },
      { name: "statut_service", label: "Statut dossier", type: "select", options: ["en_cours", "valide", "cloture"] },
      { name: "date_echeance", label: "Échéance (AAAA-MM-JJ)", type: "date" },
      { name: "commentaire", label: "Notes / accusé TEJ", type: "textarea" },
    ],
    client_messages: [
      { name: "client", label: "Client *", type: "select", source: "/api/admin/clients", valueKey: "id", textKey: (c) => c.name },
      { name: "text", label: "Réponse au client *", type: "textarea" },
    ],
    dossier_tasks: [
      { name: "dossier", label: "Dossier *", type: "select", source: "/api/admin/client_service_suivis", valueKey: "id", textKey: (d) => d.client_name + " — " + d.service_title },
      { name: "titre", label: "Titre de la tâche *", type: "text" },
      { name: "description", label: "Description", type: "textarea" },
      { name: "statut", label: "Statut", type: "select", options: ["a_faire", "en_cours", "termine"] },
      { name: "date_echeance", label: "Échéance (AAAA-MM-JJ)", type: "date" },
      { name: "repetition", label: "Répétition", type: "select", options: ["ponctuel", "mensuel", "trimestriel", "semestriel", "annuel"] },
    ],
    dossier_attachments: [
      { name: "dossier", label: "Dossier *", type: "select", source: "/api/admin/client_service_suivis", valueKey: "id", textKey: (d) => d.client_name + " — " + d.service_title },
      { name: "file", label: "Fichier *", type: "file" },
    ],
    prefactures: [
      { name: "dossier", label: "Dossier *", type: "select", source: "/api/admin/client_service_suivis", valueKey: "id", textKey: (d) => d.client_name + " — " + d.service_title },
      { name: "taux_tva", label: "Taux TVA (%)", type: "number", step: "0.01" },
    ],
    declarations: [
      { name: "client", label: "Client *", type: "select", source: "/api/admin/clients", valueKey: "id", textKey: (c) => c.name },
      { name: "type_declaration", label: "Type de déclaration *", type: "select", options: ["mensuelle", "acompte", "annuelle", "autre"] },
      { name: "periode", label: "Période (ex : Mois de Juillet 2026) *", type: "text" },
      { name: "date_echeance_legale", label: "Date limite légale *", type: "date" },
      { name: "statut", label: "Statut", type: "select", options: ["a_faire", "en_cours", "depose", "retard"] },
      { name: "montant_a_payer", label: "Montant net à payer (TND)", type: "number", step: "0.001" },
      { name: "numero_quittance_ou_tej", label: "N° quittance / accusé de dépôt", type: "text" },
      { name: "notes_collaborateur", label: "Remarques internes ou conseils", type: "textarea" },
    ],
    service_followups: [
      { name: "client", label: "Client *", type: "select", source: "/api/admin/clients", valueKey: "id", textKey: (c) => c.name },
      { name: "dossier", label: "Dossier associé *", type: "select", source: "/api/admin/client_service_suivis", valueKey: "id", textKey: (d) => d.client_name + " — " + d.service_title + " (N°" + d.id + ")" },
      { name: "type_service", label: "Service *", type: "select", source: "/api/admin/types_service", valueKey: "id", textKey: (s) => s.title },
      { name: "status", label: "Statut", type: "select", options: ["en_attente", "en_cours", "termine", "cloture", "annule"] },
      { name: "start_date", label: "Date de début (AAAA-MM-JJ)", type: "date" },
      { name: "due_date", label: "Échéance (AAAA-MM-JJ)", type: "date" },
      { name: "notes", label: "Notes", type: "textarea" },
    ],
  };

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
      { key: "dossier_label", label: "Dossier" },
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
      { key: "frequence", label: "Fréquence" },
      { key: "commentaire", label: "Notes" },
    ],
    dossier_tasks: [
      { key: "id", label: "N°" },
      { key: "client_name", label: "Client" },
      { key: "dossier_service", label: "Dossier" },
      { key: "titre", label: "Tâche" },
      { key: "statut", label: "Statut" },
      { key: "date_echeance", label: "Échéance" },
      { key: "repetition", label: "Répétition" },
    ],
    prefactures: [
      { key: "id", label: "N°" },
      { key: "client_name", label: "Client" },
      { key: "dossier_service", label: "Dossier" },
      { key: "numero", label: "Numéro" },
      { key: "date", label: "Date" },
      { key: "montant_ttc", label: "TTC (TND)" },
      { key: "statut", label: "Statut" },
    ],
    declarations: [
      { key: "id", label: "N°" },
      { key: "client_name", label: "Client" },
      { key: "type_declaration", label: "Type" },
      { key: "periode", label: "Période" },
      { key: "date_echeance_legale", label: "Échéance légale" },
      { key: "statut", label: "Statut" },
      { key: "numero_quittance_ou_tej", label: "N° quittance / TEJ" },
      { key: "montant_a_payer", label: "Montant (TND)" },
      { key: "notes_collaborateur", label: "Notes" },
    ],
    dossier_attachments: [
      { key: "id", label: "N°" },
      { key: "client_name", label: "Client" },
      { key: "dossier_service", label: "Dossier" },
      { key: "original_name", label: "Fichier" },
      { key: "category", label: "Type" },
      { key: "size", label: "Taille" },
      { key: "uploaded_by", label: "Ajouté par" },
      { key: "created_at", label: "Ajouté le" },
    ],
  };

  const DETAIL_TABLES = ["client_service_suivis", "service_followups", "dossier_tasks"];

  async function loadTab(tab) {
    const wrap = document.getElementById("tab-content");
    const detail = DETAIL_TABLES.includes(tab);
    const searchHtml = detail
      ? `<div class="tab-toolbar"><input id="id-search" placeholder="Filtrer par N° (ID)…" oninput="BalanceAdmin.searchById()" /><small>Recherche par identifiant du dossier / service / tâche</small></div>`
      : "";
    wrap.innerHTML = `<div id="tab-toolbar">${searchHtml}</div><div id="tab-table"><p>Chargement…</p></div>`;
    try {
      const data = await api(`/api/admin/${tab}`);
      renderTable(tab, data.items || []);
    } catch (e) {
      document.getElementById("tab-table").innerHTML = `<div class="alert show alert-error">${e.message}</div>`;
    }
  }

  async function searchById() {
    const val = document.getElementById("id-search").value.trim();
    try {
      const data = await api(`/api/admin/${currentTab}${val ? "?q=" + encodeURIComponent(val) : ""}`);
      renderTable(currentTab, data.items || []);
    } catch (e) {
      document.getElementById("tab-table").innerHTML = `<div class="alert show alert-error">${e.message}</div>`;
    }
  }

  function renderTable(tab, items) {
    const wrap = document.getElementById("tab-table");
    if (!items.length) {
      wrap.innerHTML = '<p style="color:#64748b">Aucun élément pour le moment.</p>';
      return;
    }
    const detail = DETAIL_TABLES.includes(tab);
    const cols = COLUMNS[tab];
    const head = cols.map((c) => `<th>${c.label}</th>`).join("");
    const body = items
      .map((item) => {
        const cells = cols
          .map((c) => {
            const value = item[c.key];
            if (c.key === "status" || c.key === "statut_paiement" || c.key === "statut_service" || c.key === "frequence" || c.key === "repetition" || c.key === "type_declaration" || (c.key === "statut" && tab !== "dossier_attachments")) {
              const opts = Array.isArray(STATUS_OPTIONS[tab])
                ? STATUS_OPTIONS[tab]
                : (STATUS_OPTIONS[tab] || {})[c.key] || [];
              if (!opts.length) return `<td>${value == null || value === "" ? "—" : escapeHtml(String(value))}</td>`;
              return `<td><select class="status-select" data-table="${tab}" data-field="${c.key}" data-id="${item.id}" onchange="BalanceAdmin.updateStatus(this)">
                ${opts.map((s) => `<option value="${s}" ${value === s ? "selected" : ""}>${s.replace("_", " ")}</option>`).join("")}
              </select></td>`;
            }
            if (c.key === "original_name" && item.url) {
              return `<td><a href="${item.url}" target="_blank" rel="noopener">${escapeHtml(String(value))}</a></td>`;
            }
            return `<td>${value == null || value === "" ? "—" : escapeHtml(String(value))}</td>`;
          })
          .join("");
        const btn = detail
          ? `<td><button class="btn btn-sm" onclick="BalanceAdmin.showDetail('${tab}', ${item.id})">Détail</button></td>`
          : `<td></td>`;
        return `<tr>${cells}${btn}</tr>`;
      })
      .join("");
    wrap.innerHTML = `<table class="admin-table"><thead><tr>${head}<th></th></tr></thead><tbody>${body}</tbody></table>`;
  }

  function statusBadge(statut) {
    const cls = { "Clôturé": "confirme", "Payé": "confirme", "Validé / déposé / conforme": "confirme", "Déposé (Validé)": "confirme", "Terminé": "confirme", "En retard": "annule", "En retard / impayé": "annule", "Annulé": "annule", "Annulée": "annule" };
    return `<span class="badge ${cls[statut] || "nouveau"}">${statut}</span>`;
  }

  async function showDetail(tab, id) {
    try {
      const data = await api(`/api/admin/detail/${tab}/${id}`);
      const it = data.item;
      document.getElementById("admin-detail-overlay").style.display = "flex";
      const wrap = document.getElementById("admin-detail-body");
      let html = "";
      if (it.type === "dossier") {
        html = `
          <h3>Dossier N°${it.id} — ${escapeHtml(it.service)}</h3>
          <p class="muted-sm">Client : <strong>${escapeHtml(it.client_name)}</strong> · ${escapeHtml(it.client_contact)}</p>
          <table class="admin-table">
            <tr><td>Service</td><td><strong>${escapeHtml(it.service)}</strong> (dans le dossier)</td></tr>
            <tr><td>Prix (TND)</td><td>${it.montant}</td></tr>
            <tr><td>Fréquence</td><td>${it.frequence}</td></tr>
            <tr><td>Échéance</td><td>${it.date_echeance}</td></tr>
            <tr><td>Statut dossier</td><td>${statusBadge(it.statut_service)}</td></tr>
            <tr><td>Statut paiement</td><td>${statusBadge(it.statut_paiement)}</td></tr>
            <tr><td>Notes</td><td>${escapeHtml(it.commentaire || "—")}</td></tr>
          </table>
          <h4>Tâches du dossier</h4>
          ${it.tasks.length ? `<ul class="task-list">${it.tasks.map((t) => `<li>${statusBadge(t.statut)} ${escapeHtml(t.titre)} — <small>${t.date_echeance} · ${t.repetition}</small></li>`).join("")}</ul>` : '<p class="muted-sm">Aucune tâche.</p>'}
          <h4>Suivi du service (dans le dossier)</h4>
          ${it.service_followups.length ? `<ul class="task-list">${it.service_followups.map((s) => `<li>${statusBadge(s.status)} ${escapeHtml(s.service)} — <small>début ${s.start_date} · fin ${s.due_date}</small>${s.tasks.length ? `<br><small>↳ Tâches : ${s.tasks.map((t) => escapeHtml(t.titre)).join(", ")}</small>` : ""}</li>`).join("")}</ul>` : '<p class="muted-sm">Aucun suivi de service lié.</p>'}
          <h4>Préfactures</h4>
          ${it.prefactures.length ? `<ul class="task-list">${it.prefactures.map((p) => `<li>${escapeHtml(p.numero)} — ${p.montant_ttc} TND — ${statusBadge(p.statut)}</li>`).join("")}</ul>` : '<p class="muted-sm">Aucune préfacture.</p>'}`;
      } else if (it.type === "service") {
        html = `
          <h3>Suivi service N°${it.id} — ${escapeHtml(it.service)}</h3>
          <p class="muted-sm">Client : <strong>${escapeHtml(it.client_name)}</strong></p>
          <table class="admin-table">
            <tr><td>Statut</td><td>${statusBadge(it.status)}</td></tr>
            <tr><td>Début / Fin</td><td>${it.start_date} → ${it.due_date}</td></tr>
            <tr><td>Notes</td><td>${escapeHtml(it.notes || "—")}</td></tr>
          </table>
          ${it.dossier ? `
            <h4>Dossier associé (service inclus dans le dossier)</h4>
            <table class="admin-table">
              <tr><td>Dossier</td><td>N°${it.dossier.id} — ${escapeHtml(it.dossier.service)}</td></tr>
              <tr><td>Prix (TND)</td><td>${it.dossier.montant}</td></tr>
              <tr><td>Fréquence</td><td>${it.dossier.frequence}</td></tr>
              <tr><td>Échéance</td><td>${it.dossier.date_echeance}</td></tr>
              <tr><td>Statut dossier</td><td>${statusBadge(it.dossier.statut_service)}</td></tr>
              <tr><td>Statut paiement</td><td>${statusBadge(it.dossier.statut_paiement)}</td></tr>
            </table>
            <h4>Tâches du service (issues du dossier)</h4>
            ${it.dossier.tasks.length ? `<ul class="task-list">${it.dossier.tasks.map((t) => `<li>${statusBadge(t.statut)} ${escapeHtml(t.titre)} — <small>${t.date_echeance} · ${t.repetition}</small></li>`).join("")}</ul>` : '<p class="muted-sm">Aucune tâche.</p>'}`
          : '<p class="muted-sm">Aucun dossier associé à ce suivi de service.</p>'}`;
      } else if (it.type === "task") {
        html = `
          <h3>Tâche N°${it.id} — ${escapeHtml(it.titre)}</h3>
          <table class="admin-table">
            <tr><td>Statut</td><td>${statusBadge(it.statut)}</td></tr>
            <tr><td>Échéance</td><td>${it.date_echeance}</td></tr>
            <tr><td>Répétition</td><td>${it.repetition}</td></tr>
            <tr><td>Description</td><td>${escapeHtml(it.description || "—")}</td></tr>
          </table>
          <h4>Dossier (tâche incluse dans le dossier)</h4>
          <table class="admin-table">
            <tr><td>Dossier</td><td>N°${it.dossier.id} — ${escapeHtml(it.dossier.service)}</td></tr>
            <tr><td>Client</td><td>${escapeHtml(it.dossier.client_name)}</td></tr>
            <tr><td>Statut dossier</td><td>${statusBadge(it.dossier.statut_service)}</td></tr>
            <tr><td>Statut paiement</td><td>${statusBadge(it.dossier.statut_paiement)}</td></tr>
            <tr><td>Prix (TND)</td><td>${it.dossier.montant}</td></tr>
          </table>`;
      }
      wrap.innerHTML = html;
    } catch (e) {
      alert(e.message);
    }
  }

  function closeDetail() {
    document.getElementById("admin-detail-overlay").style.display = "none";
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

  function fieldHtml(f) {
    const id = "cf-" + f.name;
    if (f.type === "select" && f.options) {
      const opts = f.options.map((o) => `<option value="${o}">${o.replace("_", " ")}</option>`).join("");
      return `<select id="${id}" ${f.label.includes("*") ? "required" : ""}><option value="">— Choisir —</option>${opts}</select>`;
    }
    if (f.type === "select") {
      return `<select id="${id}" ${f.label.includes("*") ? "required" : ""}><option value="">Chargement…</option></select>`;
    }
    if (f.type === "textarea") {
      return `<textarea id="${id}" rows="2"></textarea>`;
    }
    if (f.type === "file") {
      return `<input id="${id}" type="file" required />`;
    }
    return `<input id="${id}" type="${f.type}" ${f.step ? `step="${f.step}"` : ""} ${f.label.includes("*") ? "required" : ""} />`;
  }

  async function buildCreateForm() {
    const cfg = CREATE_FORMS[currentTab];
    const box = document.getElementById("create-box");
    const fields = cfg
      .map((f) => `<div class="form-group"><label for="cf-${f.name}">${f.label}</label>${fieldHtml(f)}</div>`)
      .join("");
    box.innerHTML = `<div class="card">
      <h3 style="margin:0 0 14px">Ajouter — ${currentTab.replace(/_/g, " ")}</h3>
      <form id="create-form" class="form-grid" style="margin:0">
        ${fields}
        <div class="form-group full" style="display:flex;gap:8px">
          <button class="btn" type="submit">Enregistrer</button>
          <button class="btn btn-outline" type="button" onclick="BalanceAdmin.toggleCreate()">Annuler</button>
        </div>
      </form>
    </div>`;

    for (const f of cfg) {
      if (f.type === "select" && f.source) {
        const el = document.getElementById("cf-" + f.name);
        try {
          const data = await api(f.source);
          const opts = (data.items || [])
            .map((it) => `<option value="${it[f.valueKey]}">${f.textKey(it)}</option>`)
            .join("");
          el.innerHTML = `<option value="">— Choisir —</option>${opts}`;
        } catch (e) {
          el.innerHTML = `<option value="">— Erreur de chargement —</option>`;
        }
      }
    }
    document.getElementById("create-form").addEventListener("submit", submitCreate);
  }

  async function submitCreate(e) {
    e.preventDefault();
    const cfg = CREATE_FORMS[currentTab];
    const hasFile = cfg.some((f) => f.type === "file");
    const fd = new FormData();
    const payload = {};
    for (const f of cfg) {
      const el = document.getElementById("cf-" + f.name);
      if (f.type === "file") {
        if (!el.files.length) {
          alert(`Champ requis : ${f.label}`);
          return;
        }
        fd.append(f.name, el.files[0]);
      } else {
        payload[f.name] = el.value.trim();
        if (f.label.includes("*") && !payload[f.name]) {
          alert(`Champ requis : ${f.label}`);
          return;
        }
        if (hasFile) fd.append(f.name, payload[f.name]);
      }
    }
    try {
      if (hasFile) {
        const res = await fetch(API_BASE + `/api/admin/${currentTab}`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token()}` },
          body: fd,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Erreur");
      } else {
        await api(`/api/admin/${currentTab}`, { method: "POST", body: JSON.stringify(payload) });
      }
      document.getElementById("create-box").style.display = "none";
      document.getElementById("create-box").innerHTML = "";
      loadTab(currentTab);
    } catch (err) {
      alert(err.message);
    }
  }

  function toggleCreate() {
    const box = document.getElementById("create-box");
    const shown = box.style.display !== "none";
    box.style.display = shown ? "none" : "";
    if (!shown) buildCreateForm();
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (token()) {
      api("/api/admin/devis_requests")
        .then(showPanel)
        .catch(() => sessionStorage.removeItem(TOKEN_KEY));
    }
  });

  return { login, logout, switchTab, updateStatus, toggleCreate, showDetail, closeDetail, searchById };
})();
