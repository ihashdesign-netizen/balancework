from django.db import migrations


def add_service(apps, schema_editor):
    Service = apps.get_model("core", "Service")
    Service.objects.get_or_create(
        slug="gestion-projets",
        defaults={
            "title": "Gestion & Étude de Projets",
            "short_desc": "Études de faisabilité et gestion de vos projets.",
            "description": "Étude de faisabilité, montage et gestion de vos projets : analyse financière, business plan, recherche de financement et suivi de la mise en œuvre, de l'idée à la réussite.",
            "icon": "target",
            "price_hint": "Sur devis",
        },
    )


def remove_service(apps, schema_editor):
    Service = apps.get_model("core", "Service")
    Service.objects.filter(slug="gestion-projets").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_accompagnement_startup"),
    ]

    operations = [
        migrations.RunPython(add_service, remove_service),
    ]
