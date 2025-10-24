import hashlib
import hmac
from http import HTTPStatus

import pytest
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.test.client import RequestFactory

from django_whatsapp.utils import verify_request, verify_signature


def test_verify_request_invalid_args(valid_verify_request: HttpRequest) -> None:
    """Test :func:`verify_request` parameter validation."""
    with pytest.raises(ValueError, match="verify_token"):
        verify_request(valid_verify_request, "")


def test_verify_request_invalid_mode(rf: RequestFactory) -> None:
    """Test :func:`verify_request` with an invalid verify mode."""
    request: HttpRequest = rf.get(
        "/",
        query_params={
            "hub.mode": "verify",
            "hub.challenge": "1158201444",
            "hub.verify_token": "meatyhamhock",
        },
    )

    with pytest.raises(SuspiciousOperation, match="mode"):
        verify_request(request, "meatyhamhock")


def test_verify_request_invalid_challenge(rf: RequestFactory) -> None:
    """Test :func:`verify_request` with a non-int challenge."""
    request: HttpRequest = rf.get(
        "/",
        query_params={
            "hub.mode": "subscribe",
            "hub.challenge": "CHALLENGE123",
            "hub.verify_token": "meatyhamhock",
        },
    )

    with pytest.raises(SuspiciousOperation, match="challenge"):
        verify_request(request, "meatyhamhock")


def test_verify_request_invalid_token(rf: RequestFactory) -> None:
    """Test :func:`verify_request` with an invalid verify token."""
    request: HttpRequest = rf.get(
        "/",
        query_params={
            "hub.mode": "subscribe",
            "hub.challenge": "1158201444",
            "hub.verify_token": "chickenbreast",
        },
    )

    with pytest.raises(SuspiciousOperation, match="token"):
        verify_request(request, "meatyhamhock")


def test_verify_request_valid(rf: RequestFactory) -> None:
    """Test :func:`verify_request` with a valid request."""
    request: HttpRequest = rf.get(
        "/",
        query_params={
            "hub.mode": "subscribe",
            "hub.challenge": "1158201444",
            "hub.verify_token": "meatyhamhock",
        },
    )

    response: HttpResponse = verify_request(request, "meatyhamhock")

    assert isinstance(response, HttpResponse)
    assert response.status_code == HTTPStatus.OK
    assert response.content == b"1158201444"


def test_verify_signature_missing_signature(rf: RequestFactory) -> None:
    """Test :func:`verify_signature` without a signature."""
    request: HttpRequest = rf.post("/")

    with pytest.raises(SuspiciousOperation, match="Signature not found"):
        verify_signature(request, b"app_secret")


def test_verify_signature_invalid_type(rf: RequestFactory) -> None:
    """Test :func:`verify_signature` with invalid digest type."""
    request: HttpRequest = rf.post("/", headers={"X-Hub-Signature-256": "md5=123456"})

    with pytest.raises(SuspiciousOperation, match="format"):
        verify_signature(request, b"app_secret")


def test_verify_signature_invalid_signature(rf: RequestFactory) -> None:
    """Test :func:`verify_signature` with invalid signature."""
    request: HttpRequest = rf.post("/", headers={"X-Hub-Signature-256": "sha256=123456"})

    with pytest.raises(SuspiciousOperation, match="Invalid signature"):
        verify_signature(request, b"app_secret")


def test_verify_signature_valid_signature(rf: RequestFactory) -> None:
    """Test :func:`verify_signature` with valid signature."""
    app_secret = b"app_secret"
    payload = b'{"entry": []}'
    expected_signature = hmac.new(app_secret, payload, hashlib.sha256).hexdigest()
    request: HttpRequest = rf.post(
        "/",
        data=payload,
        content_type="application/json",
        headers={"X-Hub-Signature-256": f"sha256={expected_signature}"},
    )

    verify_signature(request, b"app_secret")
