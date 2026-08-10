from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    # Pages
    path("", TemplateView.as_view(template_name="index.html"), name="accueil"),
    path("services/", TemplateView.as_view(template_name="services.html"), name="services"),
    path("devis/", TemplateView.as_view(template_name="devis.html"), name="devis"),
    path("contact/", TemplateView.as_view(template_name="contact.html"), name="contact"),
    path("rendezvous/", TemplateView.as_view(template_name="rendezvous.html"), name="rendezvous"),
    path("gestion/", TemplateView.as_view(template_name="admin.html"), name="admin_site"),
    path("espace-client/", TemplateView.as_view(template_name="espace_client.html"), name="espace_client"),

    # API publique
    path("api/services", views.api_services, name="api_services"),
    path("api/availability", views.api_availability, name="api_availability"),
    path("api/contact", views.api_contact, name="api_contact"),
    path("api/devis", views.api_devis, name="api_devis"),
    path("api/rendezvous", views.api_rendezvous, name="api_rendezvous"),

    # API espace client
    path("api/auth/register", views.api_client_register, name="api_client_register"),
    path("api/auth/login", views.api_client_login, name="api_client_login"),
    path("api/auth/logout", views.api_client_logout, name="api_client_logout"),
    path("api/client/dashboard", views.api_client_dashboard, name="api_client_dashboard"),

    # API admin (jeton Bearer)
    path("api/admin/<str:table>", views.api_admin, name="api_admin"),

    # SEO
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("robots.txt", views.robots, name="robots"),
]
