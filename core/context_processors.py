from django.conf import settings


def site_info(request):
    return {
        "site_name": settings.SITE_NAME,
        "site_url": settings.SITE_URL,
        "site_email": settings.SITE_EMAIL,
        "site_phone": settings.SITE_PHONE,
        "site_phone_raw": settings.SITE_PHONE.replace(" ", ""),
        "site_address": settings.SITE_ADDRESS,
        "site_hours": settings.SITE_HOURS,
        "currency": settings.CURRENCY,
    }
