"""WhatsApp Webhook views."""

from typing import ClassVar

from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    """View to handle WhatsApp webhook requests."""

    http_method_names: ClassVar[list[str]] = ["get", "post", "options"]

    async def get(self, request: HttpRequest) -> HttpResponse:
        """Handle a WhatsApp Verification Request."""
        raise NotImplementedError

    async def post(self, request: HttpRequest) -> HttpResponse:
        """Handle a WhatsApp Event Notification."""
        raise NotImplementedError
