from http import HTTPStatus

import pytest
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.test.client import RequestFactory

from django_whatsapp.utils import verify_request


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
