"""Mixin to validate WhatsApp signature."""

from collections.abc import Awaitable
from typing import Any

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseBase

from .utils import verify_signature


class WhatsappSignatureMixin:
    """Validate the WhatsApp signature for POST requests."""

    def dispatch(  # noqa: D102
        self,
        request: HttpRequest,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> HttpResponseBase | Awaitable[HttpResponseBase]:
        try:
            if request.method == "POST":
                verify_signature(request, app_secret=settings.WHATSAPP_APP_SECRET)
        except SuspiciousOperation as exc:
            response = HttpResponseBadRequest(str(exc))
            if self.view_is_async:  # type: ignore[attr-defined]

                async def func() -> HttpResponseBase:
                    return response

                return func()

            return response
        else:
            return super().dispatch(request, *args, **kwargs)  # type: ignore[no-any-return,misc]
