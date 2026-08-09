# Balance And Tax Safety

Site web du cabinet comptable **Balance And Tax Safety** (Tunis, Tunisie).

- Frontend : **JavaScript / HTML / CSS**
- Backend : **Python + Django**
- Base de données : **MySQL** (SQLite possible en local)
- Déploiement : Django sur un hébergeur (Railway, Render, VPS) derrière **Cloudflare** (DNS + CDN + HTTPS)
- Emails automatiques : réponse immédiate au client + notification au cabinet

## Fonctionnalités

- Page d'accueil et page services (9 pôles : comptabilité, fiscalité, sécurité sociale, déclarations, suivi de dossier, personnel, vente/achat, temps réel, facturation électronique TEJ)
- **Devis en ligne** : enregistrement + e-mail de confirmation automatique avec numéro de suivi
- **Contact** : formulaire + réponse automatique
- **Rendez-vous** : choix de date et créneau en temps réel (créneaux réservés masqués), confirmation automatique
- **Espace admin** (`/gestion/`) : suivi des devis, messages et rendez-vous, changement de statut (jeton Bearer)
- **Admin Django** (`/admin/`) : gestion complète en base
- **SEO** : meta + Open Graph + données structurées (schema.org AccountingService) + `sitemap.xml` + `robots.txt`

---

## Installation en local (macOS / Linux)

```bash
# 1. Cloner / ouvrir le dossier
cd balancework

# 2. Environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 3. Dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
#    - test local rapide : DB_ENGINE=sqlite
#    - MySQL : renseigner DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# 5. Migrations + superutilisateur
python manage.py migrate
python manage.py createsuperuser

# 6. Lancer
python manage.py runserver
#    Site : http://127.0.0.1:8000/
#    Espace admin : http://127.0.0.1:8000/gestion/  (jeton ADMIN_TOKEN)
#    Admin Django : http://127.0.0.1:8000/admin/
```

> Les emails utilisent par défaut la console (rien n'est envoyé en dev). Configurez le SMTP dans `.env` pour de vrais envois (voir plus bas).

---

## Base de données MySQL

```sql
CREATE DATABASE balancework CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'balanceuser'@'%' IDENTIFIED BY 'mot-de-passe-fort';
GRANT ALL PRIVILEGES ON balancework.* TO 'balanceuser'@'%';
FLUSH PRIVILEGES;
```

Puis dans `.env` :

```
DB_ENGINE=mysql
DB_NAME=balancework
DB_USER=balanceuser
DB_PASSWORD=mot-de-passe-fort
DB_HOST=<hôte mysql>
DB_PORT=3306
```

Si `mysqlclient` ne compile pas, le code bascule automatiquement sur `PyMySQL` (déjà dans requirements).

---

## Emails automatiques (SMTP)

Les e-mails de réponse automatique (client) et de notification (cabinet) utilisent le SMTP Django :

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.exemple.com
EMAIL_PORT=587
EMAIL_HOST_USER=contact@balancework.tn
EMAIL_HOST_PASSWORD=xxxx
EMAIL_USE_TLS=1
DEFAULT_FROM_EMAIL=Balance And Tax Safety <contact@balancework.tn>
```

---

## Déploiement : Django sur un hébergeur + Cloudflare devant

### Étape 1 — Déployer Django sur Railway (ou Render/VPS)

1. Poussez le code sur GitHub.
2. Sur **Railway** : *New Project → Deploy from GitHub* → votre repo.
   - Build : `pip install -r requirements.txt`
   - Start : `gunicorn balancework.wsgi:application --bind 0.0.0.0:$PORT --workers 3`
   - (Le fichier `Procfile` est fourni.)
3. Ajoutez une base **MySQL** (Railway MySQL) et copiez ses identifiants dans les variables d'environnement du service.
4. Variables d'environnement :

```
SECRET_KEY=<longue chaîne aléatoire>
DEBUG=0
ALLOWED_HOSTS=votre-domaine.tn,<railway-app>.up.railway.app
CSRF_TRUSTED_ORIGINS=https://votre-domaine.tn
SITE_URL=https://votre-domaine.tn/
ADMIN_TOKEN=<jeton long et aléatoire>
DB_ENGINE=mysql
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=3306
EMAIL_* = ...
```

5. Exécutez les migrations et collectez les fichiers statiques :
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
   (Sur Railway : utilisez un `Pre-deploy Command` : `python manage.py migrate && python manage.py collectstatic --noinput`)

6. Vérifiez que le site répond sur l'URL Railway (`https://xxx.up.railway.app/`).

### Étape 2 — Brancher Cloudflare (DNS + CDN + HTTPS)

1. Ajoutez votre domaine sur **Cloudflare** (Zone) et suivez les instructions pour changer les serveurs de noms chez votre registrar (`.tn`, OVH, etc.).
2. Ajoutez un enregistrement **CNAME** :
   - Nom : `@` (ou `www`)
   - Cible : `<votre-service>.up.railway.app`
   - **Proxy : activé (nuage orange)** ← indispensable
3. Section **SSL/TLS** :
   - Mode : *Full (strict)*
   - *Always Use HTTPS* : activé
   - *Minimum TLS Version* : 1.2
4. Attendez 5 à 15 minutes, puis ouvrez `https://votre-domaine.tn/`.

### Étape 3 — Vérifications finales

- `https://votre-domaine.tn/robots.txt` → doit référencer le sitemap
- `https://votre-domaine.tn/sitemap.xml` → pages du site
- Soumettez le sitemap dans **Google Search Console** pour l'indexation.

---

## Sécurité / notes

- `ADMIN_TOKEN` protège l'espace admin `/gestion/` (entêtes `Authorization: Bearer <jeton>`).
- En production (`DEBUG=0`), le site force HTTPS et active HSTS.
- Changez toujours `SECRET_KEY`, `ADMIN_TOKEN` et le mot de passe superutilisateur.
- Les e-mails de devis utilisent un numéro de suivi `#xxxxxx` affiché au client.

## Structure

```
balancework/
├── balancework/        # configuration Django (settings, urls, wsgi)
├── core/               # application : modèles, vues API, emails, admin
├── templates/          # pages HTML (Django templates, SEO)
├── static/             # CSS + JS du frontend
├── manage.py
├── requirements.txt
├── Procfile
└── .env.example
```
