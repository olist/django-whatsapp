from django.urls import include, path

urlpatterns = [
    path("", include("django_whatsapp.urls", namespace="django_whatsapp")),
]
