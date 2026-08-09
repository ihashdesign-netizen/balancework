from django.db import migrations

SERVICES = [
    {
        "slug": "conseil-fiscal",
        "title": "Expert Conseiller Fiscal",
        "short_desc": "Conseil fiscal, optimisation et représentation auprès du fisc.",
        "description": "Accompagnement fiscal personnalisé : conseil et optimisation légale, gestion des contrôles fiscaux, représentation auprès de l'administration et sécurisation de votre situation fiscale en Tunisie.",
        "icon": "user-check",
        "price_hint": "Sur devis",
    },
    {
        "slug": "tax",
        "title": "Fiscalité & Déclarations",
        "short_desc": "TVA, IS, IRPP, déclarations et conseil fiscal.",
        "description": "Gestion de vos obligations fiscales : déclarations TVA mensuelles et trimestrielles, impôt sur les sociétés (IS), IRPP, suivi des échéances et optimisation fiscale légale.",
        "icon": "calculator",
        "price_hint": "Sur devis",
    },
    {
        "slug": "safety",
        "title": "Sécurité Sociale & Paie",
        "short_desc": "CNSS, paie et gestion du personnel.",
        "description": "Gestion de la paie de vos salariés, déclarations et cotisations CNSS, attestations de travail et conformité sociale en toute sécurité.",
        "icon": "shield",
        "price_hint": "Dès 100 TND / mois",
    },
    {
        "slug": "declaration",
        "title": "Déclarations & Dépôts",
        "short_desc": "Préparation et dépôt de vos déclarations.",
        "description": "Nous préparons, vérifions et déposons l'ensemble de vos déclarations fiscales et sociales auprès des administrations concernées (fisc, CNSS), avec suivi des accusés de dépôt.",
        "icon": "file",
        "price_hint": "Dès 80 TND / dépôt",
    },
    {
        "slug": "dossier",
        "title": "Suivi de Dossier",
        "short_desc": "Suivi de vos dossiers et échéances en continu.",
        "description": "Un suivi rigoureux et transparent de chacun de vos dossiers : échéances, relances, mises à jour et comptes rendus réguliers jusqu'à la clôture.",
        "icon": "eye",
        "price_hint": "Inclus / sur devis",
    },
    {
        "slug": "personnel",
        "title": "Gestion du Personnel",
        "short_desc": "Contrats, congés, absences et paie.",
        "description": "Gestion administrative complète du personnel : contrats de travail, congés, absences, bulletins de paie et déclarations sociales associées.",
        "icon": "users",
        "price_hint": "Dès 50 TND / salarié",
    },
    {
        "slug": "vente",
        "title": "Vente / Achat",
        "short_desc": "Suivi de vos opérations d'achat et de vente.",
        "description": "Enregistrement et suivi de vos factures d'achat et de vente, rapprochements clients / fournisseurs et préparation de la TVA correspondante.",
        "icon": "cart",
        "price_hint": "Dès 120 TND / mois",
    },
    {
        "slug": "realtime",
        "title": "Suivi en Temps Réel",
        "short_desc": "Tableaux de bord et indicateurs à jour.",
        "description": "Tableaux de bord clairs et mis à jour en temps réel : trésorerie, chiffre d'affaires, charges et résultats, consultables à tout moment.",
        "icon": "trending",
        "price_hint": "Dès 150 TND / mois",
    },
    {
        "slug": "tej",
        "title": "Facturation Électronique TEJ",
        "short_desc": "Conformité à la norme tunisienne d'e-facturation.",
        "description": "Mise en conformité avec la facturation électronique obligatoire en Tunisie : transmission de vos factures via la plateforme TEJ des finances publiques, gestion des signatures électroniques et archivage conforme aux normes tunisiennes en vigueur.",
        "icon": "link",
        "price_hint": "Sur devis",
    },
    {
        "slug": "accompagnement",
        "title": "Accompagnement Start-up & Création d'Entreprise",
        "short_desc": "Création de société et accompagnement des start-ups.",
        "description": "Accompagnement complet de la création de votre entreprise en Tunisie : choix de la forme juridique, immatriculation, plan d'affaires, fiscalité des start-ups et suivi de vos premières années d'activité.",
        "icon": "rocket",
        "price_hint": "Sur devis",
    },
    {
        "slug": "gestion-projets",
        "title": "Gestion & Étude de Projets",
        "short_desc": "Études de faisabilité et gestion de vos projets.",
        "description": "Étude de faisabilité, montage et gestion de vos projets : analyse financière, business plan, recherche de financement et suivi de la mise en œuvre, de l'idée à la réussite.",
        "icon": "target",
        "price_hint": "Sur devis",
    },
]


def seed_services(apps, schema_editor):
    Service = apps.get_model("core", "Service")
    for data in SERVICES:
        Service.objects.get_or_create(slug=data["slug"], defaults=data)


def unseed_services(apps, schema_editor):
    Service = apps.get_model("core", "Service")
    Service.objects.filter(slug__in=[s["slug"] for s in SERVICES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_services, unseed_services),
    ]
