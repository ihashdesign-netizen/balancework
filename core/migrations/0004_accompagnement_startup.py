from django.db import migrations


def add_service(apps, schema_editor):
    Service = apps.get_model("core", "Service")
    Service.objects.get_or_create(
        slug="accompagnement",
        defaults={
            "title": "Accompagnement Start-up & Création d'Entreprise",
            "short_desc": "Création de société et accompagnement des start-ups.",
            "description": "Accompagnement complet de la création de votre entreprise en Tunisie : choix de la forme juridique, immatriculation, plan d'affaires, fiscalité des start-ups et suivi de vos premières années d'activité.",
            "icon": "rocket",
            "price_hint": "Sur devis",
        },
    )


def remove_service(apps, schema_editor):
    Service = apps.get_model("core", "Service")
    Service.objects.filter(slug="accompagnement").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_expert_conseiller_fiscal"),
    ]

    operations = [
        migrations.RunPython(add_service, remove_service),
    ]
