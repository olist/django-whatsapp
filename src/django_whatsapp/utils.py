"""Utility functions."""

from http import HTTPStatus

from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest, HttpResponse


def verify_request(request: HttpRequest, verify_token: str) -> HttpResponse:
    """Verify a WhatsApp Verification Request.

    Args:
        request: the actual HTTP request presumably sent by WhatsApp.
        verify_token: the Verify Token configured in the App Dashboard.
    Returns:
        :class:`HttpResponse` to send back do WhatsApp.
    Raises:
        :exc:`SuspiciousOperation` if request does not seem legit.
    """
    mode: str | None = request.GET.get("hub.mode")
    token: str | None = request.GET.get("hub.verify_token")
    challenge: str | None = request.GET.get("hub.challenge")

    if not verify_token:
        msg = "Invalid or missing verify_token"
        raise ValueError(msg)

    if mode != "subscribe":
        msg = "Invalid request mode"
        raise SuspiciousOperation(msg)

    if (challenge is None) or (not challenge.isnumeric()):
        msg = f"{challenge} is not a valid challenge"
        raise SuspiciousOperation(msg)

    if token != verify_token:
        msg = "Invalid verify token"
        raise SuspiciousOperation(msg)

    return HttpResponse(challenge, status=HTTPStatus.OK)
