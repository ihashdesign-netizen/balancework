"""Vues de l'application Balance And Tax Safety."""
import json
import secrets
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import (
    Appointment,
    AuthToken,
    Client,
    ClientServiceSuivi,
    DevisRequest,
    Message,
    Payment,
    Service,
    ServiceFollowUp,
)
from .mail import send_auto_reply_and_notify

OPENING_HOURS = range(9, 17)


def sitemap(request):
    base = settings.SITE_URL
    pages = ["", "services/", "devis/", "contact/", "rendezvous/"]
    urls = "\n".join(
        f'<url><loc>{base}{p}</loc><changefreq>monthly</changefreq><priority>{"1.0" if not p else "0.8"}</priority></url>'
        for p in pages
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>"
    )
    return HttpResponse(xml, content_type="application/xml")


def robots(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /admin/",
        "",
        f"Sitemap: {settings.SITE_URL}sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def _slots():
    slots = []
    for hour in OPENING_HOURS:
        slots.append(f"{hour:02d}:00")
        slots.append(f"{hour:02d}:30")
    return slots


def _json(data, status=200):
    return JsonResponse(data, status=status, safe=False)


def _read_body(request: HttpRequest) -> dict:
    try:
        return json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return {}


def _missing(body: dict, fields):
    return [f for f in fields if not (body.get(f) or "").strip()]


def _service_or_none(slug):
    if not slug:
        return None
    return Service.objects.filter(slug=slug).first()


def _service_title(service):
    return service.title if service else "—"


@require_GET
def api_services(request):
    services = list(Service.objects.values(
        "slug", "title", "short_desc", "description", "icon"
    ))
    return _json({"ok": True, "services": services})


@require_GET
def api_availability(request):
    day = request.GET.get("date", "")
    try:
        target = date.fromisoformat(day)
    except ValueError:
        return _json({"ok": False, "error": "Date invalide"}, 400)
    busy = set(
        Appointment.objects.filter(date=target)
        .exclude(status="annule")
        .values_list("time", flat=True)
    )
    available = [s for s in _slots() if s not in busy]
    return _json({"ok": True, "date": day, "slots": available})


@csrf_exempt
@require_POST
def api_contact(request):
    body = _read_body(request)
    missing = _missing(body, ["name", "email", "message"])
    if missing:
        return _json({"ok": False, "error": f"Champs manquants : {', '.join(missing)}"}, 400)

    Message.objects.create(
        name=body["name"].strip(),
        email=body["email"].strip(),
        phone=body.get("phone", "").strip(),
        subject=body.get("subject", "").strip(),
        message=body["message"].strip(),
    )
    send_auto_reply_and_notify(
        body["email"].strip(),
        "contact",
        [
            ("Nom", body["name"]),
            ("E-mail", body["email"]),
            ("Téléphone", body.get("phone", "")),
            ("Sujet", body.get("subject", "")),
            ("Message", body.get("message", "")),
        ],
    )
    return _json({"ok": True, "message": "Message envoyé. Réponse automatique envoyée par e-mail."})


@csrf_exempt
@require_POST
def api_devis(request):
    body = _read_body(request)
    missing = _missing(body, ["name", "email"])
    if missing:
        return _json({"ok": False, "error": f"Champs manquants : {', '.join(missing)}"}, 400)

    DevisRequest.objects.create(
        name=body["name"].strip(),
        email=body["email"].strip(),
        phone=body.get("phone", "").strip(),
        company=body.get("company", "").strip(),
        service=_service_or_none(body.get("service")),
        budget=body.get("budget", "").strip(),
        details=body.get("details", "").strip(),
    )
    send_auto_reply_and_notify(
        body["email"].strip(),
        "devis",
        [
            ("Nom", body["name"]),
            ("E-mail", body["email"]),
            ("Téléphone", body.get("phone", "")),
            ("Société", body.get("company", "")),
            ("Service", _service_title(_service_or_none(body.get("service")))),
            ("Budget", body.get("budget", "")),
            ("Détails", body.get("details", "")),
        ],
    )
    return _json({"ok": True, "message": "Demande de devis enregistrée. Réponse automatique envoyée par e-mail."})


@csrf_exempt
@require_POST
def api_rendezvous(request):
    body = _read_body(request)
    missing = _missing(body, ["name", "email", "date", "time"])
    if missing:
        return _json({"ok": False, "error": f"Champs manquants : {', '.join(missing)}"}, 400)

    try:
        day = date.fromisoformat(body["date"])
    except ValueError:
        return _json({"ok": False, "error": "Date invalide"}, 400)

    if day <= date.today():
        return _json({"ok": False, "error": "Choisissez une date future."}, 400)

    time = body["time"].strip()
    busy = Appointment.objects.filter(date=day).exclude(status="annule").values_list("time", flat=True)
    if time in busy:
        return _json(
            {"ok": False, "error": "Ce créneau vient d'être réservé. Veuillez en choisir un autre."}, 409
        )

    Appointment.objects.create(
        name=body["name"].strip(),
        email=body["email"].strip(),
        phone=body.get("phone", "").strip(),
        service=_service_or_none(body.get("service")),
        date=day,
        time=time,
        notes=body.get("notes", "").strip(),
    )
    send_auto_reply_and_notify(
        body["email"].strip(),
        "rendezvous",
        [
            ("Nom", body["name"]),
            ("E-mail", body["email"]),
            ("Téléphone", body.get("phone", "")),
            ("Service", _service_title(_service_or_none(body.get("service")))),
            ("Date", day.strftime("%d/%m/%Y")),
            ("Heure", time),
            ("Notes", body.get("notes", "")),
        ],
    )
    return _json({
        "ok": True,
        "message": f"Rendez-vous demandé le {day.strftime('%d/%m/%Y')} à {time}. Confirmation envoyée par e-mail.",
    })


# ---------------- API Client (Espace client) ----------------

def _bearer_token(request) -> str:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip()
    return ""


def _client_from_request(request):
    token = AuthToken.objects.filter(key=_bearer_token(request)).select_related("user").first()
    if not token:
        return None
    client = Client.objects.filter(user=token.user).first()
    return client


@csrf_exempt
def api_client_register(request):
    if request.method != "POST":
        return _json({"ok": False, "error": "Méthode non autorisée"}, 405)
    body = _read_body(request)
    name = (body.get("name") or "").strip()
    prenom = (body.get("prenom") or "").strip()
    email = (body.get("email") or "").strip().lower()
    phone = (body.get("phone") or "").strip()
    password = body.get("password") or ""
    matricule = (body.get("matricule_fiscale") or "").strip()
    cin = (body.get("cin") or "").strip()

    missing = [f for f in ("name", "prenom", "email", "phone", "password") if not body.get(f)]
    if missing:
        return _json({"ok": False, "error": f"Champs manquants : {', '.join(missing)}"}, 400)
    if not matricule and not cin:
        return _json({"ok": False, "error": "Indiquez au moins le matricule fiscal ou le numéro de carte d'identité."}, 400)
    if User.objects.filter(username=email).exists():
        return _json({"ok": False, "error": "Un compte existe déjà avec cet e-mail."}, 400)

    user = User.objects.create_user(username=email, email=email, first_name=prenom, last_name=name, password=password)
    client = Client.objects.create(
        user=user, name=name, prenom=prenom, email=email, phone=phone,
        matricule_fiscale=matricule, cin=cin,
    )
    token = AuthToken.objects.create(key=secrets.token_hex(32), user=user)
    return _json({"ok": True, "token": token.key, "client": _client_payload(client)})


@csrf_exempt
def api_client_login(request):
    if request.method != "POST":
        return _json({"ok": False, "error": "Méthode non autorisée"}, 405)
    body = _read_body(request)
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    user = authenticate(username=email, password=password)
    if not user or not hasattr(user, "client"):
        return _json({"ok": False, "error": "Identifiants invalides."}, 401)
    token, created = AuthToken.objects.get_or_create(user=user)
    token.key = secrets.token_hex(32)
    token.save(update_fields=["key"])
    return _json({"ok": True, "token": token.key, "client": _client_payload(user.client)})


@csrf_exempt
def api_client_logout(request):
    AuthToken.objects.filter(key=_bearer_token(request)).delete()
    return _json({"ok": True})


@csrf_exempt
def api_client_dashboard(request):
    client = _client_from_request(request)
    if not client:
        return _json({"ok": False, "error": "Non autorisé"}, 401)
    suivis = []
    for s in ClientServiceSuivi.objects.filter(client=client):
        suivis.append({
            "id": s.id,
            "service": s.service_title,
            "montant": str(s.montant),
            "statut_paiement": s.get_statut_paiement_display(),
            "statut_service": s.get_statut_service_display(),
            "date_echeance": s.date_echeance.strftime("%d/%m/%Y"),
            "commentaire": s.commentaire,
        })
    return _json({"ok": True, "client": _client_payload(client), "suivis": suivis})


def _client_payload(client):
    return {
        "name": f"{client.prenom} {client.name}".strip(),
        "email": client.email,
        "phone": client.phone,
        "matricule_fiscale": client.matricule_fiscale,
        "cin": client.cin,
    }


# ---------------- API Admin (jeton Bearer) ----------------

def _authorized(request) -> bool:
    token = request.headers.get("Authorization", "")
    return bool(settings.ADMIN_TOKEN) and token == f"Bearer {settings.ADMIN_TOKEN}"


TABLES = {
    "devis_requests": (DevisRequest, ["id", "name", "email", "phone", "company", "budget", "details", "status", "created_at"], "service_title"),
    "appointments": (Appointment, ["id", "name", "email", "phone", "date", "time", "notes", "status"], "service_title"),
    "messages": (Message, ["id", "name", "email", "phone", "subject", "message", "status", "created_at"], None),
    "clients": (Client, ["id", "name", "email", "phone", "company", "notes", "created_at"], None),
    "payments": (Payment, ["id", "client_name", "amount", "date", "status", "method", "notes", "created_at"], None),
    "service_followups": (ServiceFollowUp, ["id", "client_name", "service_title", "status", "start_date", "due_date", "notes", "created_at"], None),
    "types_service": (Service, ["id", "title", "slug", "short_desc"], None),
    "client_service_suivis": (ClientServiceSuivi, ["id", "client_name", "service_title", "montant", "statut_paiement", "statut_service", "date_echeance", "commentaire"], None),
}


@csrf_exempt
def api_admin(request, table):
    if not _authorized(request):
        return _json({"ok": False, "error": "Non autorisé"}, 401)
    spec = TABLES.get(table)
    if not spec:
        return _json({"ok": False, "error": "Table inconnue"}, 400)

    model, fields, extra = spec
    if request.method == "GET":
        items = []
        for obj in model.objects.all():
            item = {f: getattr(obj, f, "") for f in fields}
            if extra:
                item[extra] = getattr(obj, extra, "—")
            items.append(item)
        return _json({"ok": True, "items": items})

    if request.method == "PUT":
        body = _read_body(request)
        try:
            obj = model.objects.get(pk=int(body.get("id", 0)))
        except (ValueError, model.DoesNotExist):
            return _json({"ok": False, "error": "Élément introuvable"}, 404)
        field = body.get("field", "status")
        choices_attr = {
            "status": "STATUS_CHOICES",
            "statut_paiement": "STATUT_PAIEMENT_CHOICES",
            "statut_service": "STATUT_SERVICE_CHOICES",
        }.get(field)
        if not choices_attr or not hasattr(obj, field):
            return _json({"ok": False, "error": "Champ invalide"}, 400)
        value = body.get("status", "")
        valid = {s for s, _ in getattr(obj, choices_attr, [])}
        if value not in valid:
            return _json({"ok": False, "error": "Statut invalide"}, 400)
        setattr(obj, field, value)
        obj.save(update_fields=[field])
        return _json({"ok": True})

    return _json({"ok": False, "error": "Méthode non autorisée"}, 405)
