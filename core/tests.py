import json
from datetime import date, timedelta

from django.test import TestCase, override_settings

from .models import (
    Appointment,
    Client,
    ClientMessage,
    ClientServiceSuivi,
    DevisRequest,
    DossierTask,
    Message,
    Service,
)


class ApiServicesTests(TestCase):
    def test_services_list(self):
        res = self.client.get("/api/services")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["ok"])
        self.assertGreaterEqual(len(data["services"]), 9)
        slugs = [s["slug"] for s in data["services"]]
        self.assertIn("conseil-fiscal", slugs)
        self.assertNotIn("balance", slugs)
        self.assertIn("tax", slugs)
        self.assertIn("safety", slugs)
        self.assertIn("tej", slugs)
        self.assertIn("accompagnement", slugs)


class ApiFormsTests(TestCase):
    def test_contact(self):
        res = self.client.post(
            "/api/contact",
            data=json.dumps({"name": "Hajer", "email": "h@test.tn", "message": "Bonjour"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["ok"])
        self.assertEqual(Message.objects.count(), 1)

    def test_contact_missing_fields(self):
        res = self.client.post(
            "/api/contact",
            data=json.dumps({"name": "Hajer"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_devis(self):
        res = self.client.post(
            "/api/devis",
            data=json.dumps({"name": "Client", "email": "c@test.tn", "service": "tax"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["ok"])
        devis = DevisRequest.objects.get()
        self.assertEqual(devis.service.slug, "tax")
        self.assertEqual(devis.status, "nouveau")

    def test_rendezvous_and_conflict(self):
        day = (date.today() + timedelta(days=2)).isoformat()
        payload = {"name": "R", "email": "r@test.tn", "date": day, "time": "10:30"}
        ok = self.client.post("/api/rendezvous", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(ok.status_code, 200)
        conflict = self.client.post("/api/rendezvous", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(Appointment.objects.count(), 1)


class ApiAdminTests(TestCase):
    @override_settings(ADMIN_TOKEN="secret-test")
    def test_requires_token(self):
        res = self.client.get("/api/admin/devis_requests")
        self.assertEqual(res.status_code, 401)

    @override_settings(ADMIN_TOKEN="secret-test")
    def test_list_and_update_status(self):
        DevisRequest.objects.create(name="A", email="a@test.tn")
        headers = {"HTTP_AUTHORIZATION": "Bearer secret-test"}

        res = self.client.get("/api/admin/devis_requests", **headers)
        self.assertEqual(res.status_code, 200)
        item = res.json()["items"][0]
        self.assertEqual(item["name"], "A")

        res = self.client.put(
            "/api/admin/devis_requests",
            data=json.dumps({"id": item["id"], "status": "traite"}),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["ok"])
        self.assertEqual(DevisRequest.objects.get().status, "traite")


class SeoTests(TestCase):
    def test_sitemap_and_robots(self):
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, "<urlset")
        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertContains(robots, "sitemap.xml")


@override_settings(ADMIN_TOKEN="secret-test")
class ServiceCrudAdminTests(TestCase):
    def setUp(self):
        self.h = {"HTTP_AUTHORIZATION": "Bearer secret-test"}

    def test_create_update_subservice_delete(self):
        res = self.client.post(
            "/api/admin/types_service",
            data=json.dumps({"title": "Audit Comptable", "slug": "audit-comptable", "short_desc": "Audit", "description": "Audit complet", "price_hint": "Sur devis", "icon": "clipboard"}),
            content_type="application/json",
            **self.h,
        )
        self.assertEqual(res.status_code, 200)
        parent_id = res.json()["id"]
        parent = Service.objects.get(pk=parent_id)
        self.assertIsNone(parent.parent)

        res = self.client.post(
            "/api/admin/types_service",
            data=json.dumps({"title": "Audit Externe", "slug": "audit-externe", "short_desc": "AE", "parent": str(parent_id)}),
            content_type="application/json",
            **self.h,
        )
        self.assertEqual(res.status_code, 200)
        sub = Service.objects.get(pk=res.json()["id"])
        self.assertEqual(sub.parent_id, parent_id)

        res = self.client.put(
            "/api/admin/types_service",
            data=json.dumps({"id": sub.id, "field": "title", "status": "Audit Externe Complet"}),
            content_type="application/json",
            **self.h,
        )
        self.assertEqual(res.status_code, 200)
        sub.refresh_from_db()
        self.assertEqual(sub.title, "Audit Externe Complet")

        res = self.client.delete("/api/admin/types_service", data=json.dumps({"id": parent_id}), content_type="application/json", **self.h)
        self.assertEqual(res.status_code, 400)

        res = self.client.delete("/api/admin/types_service", data=json.dumps({"id": sub.id}), content_type="application/json", **self.h)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Service.objects.filter(pk=sub.id).exists())

        res = self.client.delete("/api/admin/types_service", data=json.dumps({"id": parent_id}), content_type="application/json", **self.h)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Service.objects.filter(pk=parent_id).exists())

    def test_cannot_delete_service_used_by_dossier(self):
        client = Client.objects.create(name="C", email="c@test.tn", phone="1")
        svc = Service.objects.create(title="S", slug="s", short_desc="d", description="x")
        ClientServiceSuivi.objects.create(client=client, type_service=svc)
        res = self.client.delete("/api/admin/types_service", data=json.dumps({"id": svc.id}), content_type="application/json", **self.h)
        self.assertEqual(res.status_code, 400)
        self.assertTrue(Service.objects.filter(pk=svc.id).exists())


class ClientMessageContextTests(TestCase):
    def setUp(self):
        res = self.client.post(
            "/api/auth/register",
            data=json.dumps({"name": "Doe", "prenom": "Jane", "email": "j@test.tn", "phone": "123", "matricule_fiscale": "1574T", "password": "password123"}),
            content_type="application/json",
        )
        self.token = res.json()["token"]
        self.client_model = Client.objects.get(email="j@test.tn")
        self.svc = Service.objects.create(title="Fiscalité", slug="fiscal", short_desc="f", description="x")
        self.dossier = ClientServiceSuivi.objects.create(client=self.client_model, type_service=self.svc, montant=100)
        self.h = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

    def test_send_message_linked_to_dossier_and_task(self):
        task = DossierTask.objects.create(dossier=self.dossier, titre="Déposer la TVA")
        res = self.client.post(
            "/api/client/messages",
            data=json.dumps({"text": "Où en est la déclaration ?", "dossier": str(self.dossier.id), "task": str(task.id)}),
            content_type="application/json",
            **self.h,
        )
        self.assertEqual(res.status_code, 200)
        msg = ClientMessage.objects.get()
        self.assertEqual(msg.dossier_id, self.dossier.id)
        self.assertEqual(msg.task_id, task.id)
        self.assertEqual(msg.service_id, self.svc.id)
        self.assertEqual(msg.context_label, f"Fiscalité (N°{self.dossier.id}) · Tâche : Déposer la TVA")

    def test_filter_messages_by_dossier(self):
        DossierTask.objects.create(dossier=self.dossier, titre="Déposer la TVA")
        self.client.post(
            "/api/client/messages",
            data=json.dumps({"text": "Suivi dossier", "dossier": str(self.dossier.id)}),
            content_type="application/json",
            **self.h,
        )
        res = self.client.get(f"/api/client/messages?dossier={self.dossier.id}", **self.h)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["messages"]), 1)
        self.assertEqual(res.json()["messages"][0]["dossier_service"], f"Fiscalité (N°{self.dossier.id})")

    def test_reject_task_of_another_dossier(self):
        other = ClientServiceSuivi.objects.create(client=self.client_model, type_service=self.svc)
        task2 = DossierTask.objects.create(dossier=other, titre="Autre tâche")
        res = self.client.post(
            "/api/client/messages",
            data=json.dumps({"text": "x", "dossier": str(self.dossier.id), "task": str(task2.id)}),
            content_type="application/json",
            **self.h,
        )
        self.assertEqual(res.status_code, 400)
