"""WhatsApp Webhook views."""

from typing import ClassVar

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .utils import verify_request


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    """View to handle WhatsApp webhook requests."""

    http_method_names: list[str] = ["get", "post", "options"]  # noqa: RUF012

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle a WhatsApp Verification Request."""
        try:
            return verify_request(request, verify_token=settings.WHATSAPP_VERIFY_TOKEN)
        except SuspiciousOperation:
            return HttpResponseBadRequest()

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle a WhatsApp Event Notification."""
        raise NotImplementedError


@method_decorator(csrf_exempt, name="dispatch")
class AsyncWebhookView(View):
    """View to handle WhatsApp webhook requests."""

    http_method_names: list[str] = ["get", "post", "options"]  # noqa: RUF012

    async def get(self, request: HttpRequest) -> HttpResponse:
        """Handle a WhatsApp Verification Request."""
        try:
            return verify_request(request, verify_token=settings.WHATSAPP_VERIFY_TOKEN)
        except SuspiciousOperation:
            return HttpResponseBadRequest()

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle a WhatsApp Event Notification."""
        raise NotImplementedError
