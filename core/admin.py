from django.contrib import admin

from .models import Appointment, DevisRequest, Message, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "price_hint")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(DevisRequest)
class DevisRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service_title", "budget", "status", "created_at")
    list_filter = ("status", "service", "created_at")
    search_fields = ("name", "email", "company")
    list_editable = ("status",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "message")
    list_editable = ("status",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date", "time", "service_title", "status")
    list_filter = ("status", "date", "service")
    search_fields = ("name", "email", "phone")
    list_editable = ("status",)
