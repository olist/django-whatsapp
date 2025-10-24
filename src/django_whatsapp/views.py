"""WhatsApp Webhook views."""

from collections.abc import Awaitable
from typing import overload

from asgiref.sync import iscoroutinefunction
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.utils.functional import classproperty
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .mixins import WhatsappSignatureMixin
from .utils import verify_request


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(WhatsappSignatureMixin, View):  # type: ignore[misc]
    """View to handle WhatsApp webhook requests."""

    http_method_names: list[str] = ["get", "post", "options"]  # noqa: RUF012

    @classproperty
    def view_is_async(cls: type["WebhookView"]) -> bool:  # noqa: N805
        """Validate if view is async based on POST method."""
        handlers = [
            getattr(cls, method)
            for method in cls.http_method_names
            if (method not in ["options", "get"] and hasattr(cls, method))
        ]
        if not handlers:
            return False
        is_async = iscoroutinefunction(handlers[0])
        if not all(iscoroutinefunction(h) == is_async for h in handlers[1:]):
            msg = f"{cls.__qualname__} HTTP handlers must either be all sync or all async."
            raise ImproperlyConfigured(msg)
        return is_async

    @overload
    def get(self, request: ASGIRequest) -> Awaitable[HttpResponse]:
        pass

    @overload
    def get(self, request: WSGIRequest) -> HttpResponse:
        pass

    def get(self, request: HttpRequest) -> HttpResponse | Awaitable[HttpResponse]:
        """Handle a WhatsApp Verification Request."""
        try:
            response = verify_request(request, verify_token=settings.WHATSAPP_VERIFY_TOKEN)
        except SuspiciousOperation:
            response = HttpResponseBadRequest()

        if self.view_is_async:

            async def func() -> HttpResponse:
                return response

            return func()

        return response
