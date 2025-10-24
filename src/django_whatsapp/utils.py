"""Utility functions."""

import hashlib
import hmac
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


def verify_signature(request: HttpRequest, app_secret: bytes) -> None:
    """Verify a WhatsApp request signature.

    Args:
        request: the actual HTTP request presumably sent by WhatsApp.
        app_secret: the App Secret presumably used to sign the request.
    Raises:
        :exc:`SuspiciousOperation` if request does not seem legit.
    """
    try:
        signature: str = request.headers["X-Hub-Signature-256"]
    except KeyError as exc:
        msg = "Signature not found in HTTP request"
        raise SuspiciousOperation(msg) from exc

    if not signature.startswith("sha256="):
        msg = "Invalid signature format"
        raise SuspiciousOperation(msg)

    signature = signature.removeprefix("sha256=")
    expected_signature = hmac.new(app_secret, request.body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        msg = "Invalid signature"
        raise SuspiciousOperation(msg)
