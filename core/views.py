"""Vues de l'application Balance And Tax Safety."""
import json
from datetime import date, timedelta

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Appointment, Client, DevisRequest, Message, Payment, Service, ServiceFollowUp
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
        status = body.get("status", "")
        valid = {s for s, _ in getattr(obj, "STATUS_CHOICES", [])}
        if status not in valid:
            return _json({"ok": False, "error": "Statut invalide"}, 400)
        obj.status = status
        obj.save(update_fields=["status"])
        return _json({"ok": True})

    return _json({"ok": False, "error": "Méthode non autorisée"}, 405)
