"""Emails automatiques : réponse au client + notification du cabinet."""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def _base_html(title, intro):
    return f"""<!doctype html>
<html lang="fr">
<body style="margin:0;padding:0;font-family:Helvetica,Arial,sans-serif;background:#f4f6f8">
  <table role="presentation" width="100%" style="background:#f4f6f8;padding:24px 0">
    <tr><td align="center">
      <table role="presentation" width="560" style="background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0">
        <tr>
          <td style="background:#0f766e;padding:28px 32px">
            <h1 style="margin:0;color:#ffffff;font-size:22px">{settings.SITE_NAME}</h1>
            <p style="margin:6px 0 0;color:#d9f3ef;font-size:13px">Expert conseiller fiscal · Tunisie</p>
          </td>
        </tr>
        <tr>
          <td style="padding:32px">
            {intro}
          </td>
        </tr>
        <tr>
          <td style="padding:20px 32px;background:#f8fafc;border-top:1px solid #e2e8f0">
            <p style="margin:0;color:#64748b;font-size:12px">© {settings.SITE_NAME} — Tunis, Tunisie.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def build_automatic_reply(name, kind):
    """Réponse automatique immédiate envoyée au client."""
    titles = {
        "devis": "Demande de devis reçue",
        "rendezvous": "Demande de rendez-vous reçue",
        "contact": "Message reçu",
    }
    intros = {
        "devis": (
            "Nous avons bien reçu votre demande de devis. Notre équipe l'étudie et vous enverra "
            "une proposition détaillée sous 24h ouvrées."
        ),
        "rendezvous": (
            "Nous avons bien reçu votre demande de rendez-vous. Un conseiller vous confirmera "
            "le créneau par téléphone ou e-mail."
        ),
        "contact": "Nous avons bien reçu votre message. Un conseiller vous répondra dans les plus brefs délais.",
    }
    intro = f"""
        <h2 style="margin:0 0 12px;color:#0f172a;font-size:18px">Bonjour {name},</h2>
        <p style="margin:0 0 16px;color:#334155;font-size:15px;line-height:1.6">{intros[kind]}</p>
        <p style="margin:0 0 24px;color:#334155;font-size:15px;line-height:1.6">
          Votre demande porte le numéro de suivi <strong style="color:#0f766e">#{id(name)}</strong>.
          Conservez-le pour toute correspondance ultérieure.
        </p>
        <table role="presentation" width="100%" style="background:#f0fdfa;border-left:4px solid #0f766e;padding:14px 18px">
          <tr><td style="font-size:13px;color:#134e4a;line-height:1.6">
            <strong>Horaires :</strong> {settings.SITE_HOURS}<br>
            <strong>Téléphone :</strong> {settings.SITE_PHONE} · <strong>Email :</strong> {settings.SITE_EMAIL}
          </td></tr>
        </table>"""
    return titles[kind], _base_html(titles[kind], intro)


def build_admin_notification(kind, rows):
    """Notification envoyée au cabinet (résumé des nouvelles demandes)."""
    titles = {
        "devis": "Nouvelle demande de devis",
        "rendezvous": "Nouvelle demande de rendez-vous",
        "contact": "Nouveau message",
    }
    cells = "".join(
        f'<tr><td style="padding:8px 12px;color:#475569;font-size:13px">{k}</td>'
        f'<td style="padding:8px 12px;color:#0f172a;font-size:13px"><strong>{v or "—"}</strong></td></tr>'
        for k, v in rows
    )
    intro = (
        f'<h2 style="margin:0 0 16px;color:#0f172a;font-size:17px">{titles[kind]}</h2>'
        f'<table role="presentation" width="100%">{cells}</table>'
    )
    return f"[{settings.SITE_NAME}] {titles[kind]}", _base_html(titles[kind], intro)


def send(to, subject, html):
    """Envoi d'un e-mail HTML. Retourne False si la config email est absente."""
    if not settings.EMAIL_HOST:
        return False
    message = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [to])
    message.attach_alternative(html, "text/html")
    message.send()
    return True


def id(name):
    """Petit numéro de suivi stable basé sur le nom."""
    return abs(hash(name.lower())) % 1000000


def send_auto_reply_and_notify(to, kind, rows):
    subject, html = build_automatic_reply(to, kind)
    send(to, subject, html)
    admin_subject, admin_html = build_admin_notification(kind, rows)
    send(settings.SITE_EMAIL, admin_subject, admin_html)
