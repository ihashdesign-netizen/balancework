from django.contrib.auth.models import User
from django.db import models


class Service(models.Model):
    """Prestation proposée par le cabinet."""

    slug = models.SlugField(unique=True, verbose_name="Identifiant")
    title = models.CharField(max_length=120, verbose_name="Titre")
    short_desc = models.CharField(max_length=255, verbose_name="Résumé")
    description = models.TextField(verbose_name="Description")
    icon = models.CharField(max_length=30, default="briefcase", verbose_name="Icône")
    price_hint = models.CharField(max_length=80, blank=True, verbose_name="Indication tarifaire")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title


class DevisRequest(models.Model):
    """Demande de devis envoyée depuis le site."""

    STATUS_CHOICES = [
        ("nouveau", "Nouveau"),
        ("en_cours", "En cours"),
        ("traite", "Traité"),
        ("annule", "Annulé"),
    ]
    name = models.CharField(max_length=120, verbose_name="Nom")
    email = models.EmailField(verbose_name="E-mail")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    company = models.CharField(max_length=120, blank=True, verbose_name="Société")
    service = models.ForeignKey(
        Service, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Service"
    )
    budget = models.CharField(max_length=80, blank=True, verbose_name="Budget estimé")
    details = models.TextField(blank=True, verbose_name="Détails")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="nouveau", verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Reçu le")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Demande de devis"
        verbose_name_plural = "Demandes de devis"

    def __str__(self):
        return f"Devis {self.name} ({self.created_at:%d/%m/%Y})"

    @property
    def service_title(self):
        return self.service.title if self.service else "—"


class Message(models.Model):
    """Message envoyé via la page contact."""

    STATUS_CHOICES = [
        ("nouveau", "Nouveau"),
        ("traite", "Traité"),
        ("annule", "Annulé"),
    ]
    name = models.CharField(max_length=120, verbose_name="Nom")
    email = models.EmailField(verbose_name="E-mail")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    subject = models.CharField(max_length=200, blank=True, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="nouveau", verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Reçu le")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.subject or 'Sans sujet'} — {self.name}"


class Appointment(models.Model):
    """Demande de rendez-vous."""

    STATUS_CHOICES = [
        ("confirme", "Confirmé"),
        ("en_attente", "En attente"),
        ("annule", "Annulé"),
    ]
    name = models.CharField(max_length=120, verbose_name="Nom")
    email = models.EmailField(verbose_name="E-mail")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    service = models.ForeignKey(
        Service, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Service"
    )
    date = models.DateField(verbose_name="Date")
    time = models.CharField(max_length=5, verbose_name="Heure")
    notes = models.TextField(blank=True, verbose_name="Notes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirme", verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Demandé le")

    class Meta:
        ordering = ["date", "time"]
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"

    def __str__(self):
        return f"{self.name} — {self.date} à {self.time}"

    @property
    def service_title(self):
        return self.service.title if self.service else "—"


class Client(models.Model):
    """Client du cabinet (espace admin + espace client)."""

    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Compte utilisateur"
    )
    name = models.CharField(max_length=120, verbose_name="Nom")
    prenom = models.CharField(max_length=120, blank=True, verbose_name="Prénom")
    email = models.EmailField(verbose_name="E-mail")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    company = models.CharField(max_length=120, blank=True, verbose_name="Société")
    matricule_fiscale = models.CharField(max_length=100, blank=True, verbose_name="Matricule fiscale")
    cin = models.CharField(max_length=8, blank=True, verbose_name="Numéro de carte d'identité")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ajouté le")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.prenom or self.name} {self.name} ({self.company or self.matricule_fiscale or '—'})"


class ClientServiceSuivi(models.Model):
    """Suivi d'un dossier / service pour un client (Balance & Safety)."""

    STATUT_PAIEMENT_CHOICES = [
        ("en_attente", "En attente"),
        ("paye", "Payé"),
        ("retard", "En retard / impayé"),
    ]
    STATUT_SERVICE_CHOICES = [
        ("en_cours", "En cours de traitement"),
        ("valide", "Validé / déposé / conforme"),
        ("cloture", "Clôturé"),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="services", verbose_name="Client")
    type_service = models.ForeignKey(
        Service, null=True, blank=True, on_delete=models.PROTECT, verbose_name="Type de service"
    )
    montant = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Montant (TND)")
    statut_paiement = models.CharField(max_length=20, choices=STATUT_PAIEMENT_CHOICES, default="en_attente", verbose_name="Statut de paiement")
    statut_service = models.CharField(max_length=20, choices=STATUT_SERVICE_CHOICES, default="en_cours", verbose_name="Suivi du service")
    date_echeance = models.DateField(verbose_name="Échéance fiscale / sociale")
    commentaire = models.TextField(blank=True, verbose_name="Notes / remarques (ex : accusé TEJ)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        ordering = ["date_echeance", "-id"]
        verbose_name = "Suivi & paiement client"
        verbose_name_plural = "Suivis & paiements clients"

    def __str__(self):
        return f"{self.client.name} — {self.type_service or '—'}"

    @property
    def client_name(self):
        return self.client.name

    @property
    def service_title(self):
        return self.type_service.title if self.type_service else "—"


class AuthToken(models.Model):
    """Jeton d'accès à l'espace client."""

    key = models.CharField(max_length=64, unique=True, verbose_name="Jeton")
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    def __str__(self):
        return f"Token {self.user.username}"


class Payment(models.Model):
    """Paiement d'un client."""

    STATUS_CHOICES = [
        ("en_attente", "En attente"),
        ("partiel", "Partiel"),
        ("paye", "Payé"),
        ("retard", "En retard"),
        ("annule", "Annulé"),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant (TND)")
    date = models.DateField(verbose_name="Date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en_attente", verbose_name="Statut")
    method = models.CharField(max_length=80, blank=True, verbose_name="Mode de paiement")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"

    def __str__(self):
        return f"{self.amount} TND — {self.client.name} ({self.date})"

    @property
    def client_name(self):
        return self.client.name


class ServiceFollowUp(models.Model):
    """Suivi d'un service souscrit par un client."""

    STATUS_CHOICES = [
        ("en_attente", "En attente"),
        ("en_cours", "En cours"),
        ("termine", "Terminé"),
        ("cloture", "Clôturé"),
        ("annule", "Annulé"),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    service = models.ForeignKey(
        Service, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Service"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en_attente", verbose_name="Statut")
    start_date = models.DateField(null=True, blank=True, verbose_name="Date de début")
    due_date = models.DateField(null=True, blank=True, verbose_name="Échéance")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Suivi de service"
        verbose_name_plural = "Suivis de service"

    def __str__(self):
        return f"{self.client.name} — {self.service or '—'}"

    @property
    def client_name(self):
        return self.client.name

    @property
    def service_title(self):
        return self.service.title if self.service else "—"
