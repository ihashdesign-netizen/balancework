from django.db import migrations


def update_services(apps, schema_editor):
    Service = apps.get_model("core", "Service")
    Service.objects.filter(slug="balance").delete()
    Service.objects.get_or_create(
        slug="conseil-fiscal",
        defaults={
            "title": "Expert Conseiller Fiscal",
            "short_desc": "Conseil fiscal, optimisation et représentation auprès du fisc.",
            "description": "Accompagnement fiscal personnalisé : conseil et optimisation légale, gestion des contrôles fiscaux, représentation auprès de l'administration et sécurisation de votre situation fiscale en Tunisie.",
            "icon": "user-check",
            "price_hint": "Sur devis",
        },
    )


def revert(apps, schema_editor):
    Service = apps.get_model("core", "Service")
    Service.objects.filter(slug="conseil-fiscal").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_seed_services"),
    ]

    operations = [
        migrations.RunPython(update_services, revert),
    ]
