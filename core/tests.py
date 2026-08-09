import json
from datetime import date, timedelta

from django.test import TestCase, override_settings

from .models import Appointment, DevisRequest, Message


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
