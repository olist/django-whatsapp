from collections.abc import Generator
from typing import Any

import pytest
from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest
from django.test import override_settings
from django.test.client import AsyncRequestFactory, RequestFactory


@pytest.fixture(autouse=True)
def _settings() -> Generator[None, Any, None]:
    with override_settings(WHATSAPP_VERIFY_TOKEN="meatyhamhock"):  # noqa: S106
        yield


@pytest.fixture
def valid_verify_request(rf: RequestFactory) -> WSGIRequest:
    """A valid verify request."""
    return rf.get(
        "/",
        query_params={
            "hub.mode": "subscribe",
            "hub.challenge": "1158201444",
            "hub.verify_token": "meatyhamhock",
        },
    )


@pytest.fixture
def avalid_verify_request(async_rf: AsyncRequestFactory) -> ASGIRequest:
    """A valid verify request."""
    return async_rf.get(
        "/",
        query_params={
            "hub.mode": "subscribe",
            "hub.challenge": "1158201444",
            "hub.verify_token": "meatyhamhock",
        },
    )
