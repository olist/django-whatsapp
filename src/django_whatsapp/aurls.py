from django.urls import path

from . import views

app_name = "django_whatsapp"

urlpatterns = [
    path("", views.AsyncWebhookView.as_view(), name="webhook"),
]
