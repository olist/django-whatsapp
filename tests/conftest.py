from collections.abc import Generator
from typing import Any

import pytest
from django.http import HttpRequest
from django.test import override_settings
from django.test.client import RequestFactory


@pytest.fixture(autouse=True)
def _settings() -> Generator[None, Any, None]:
    with override_settings(WHATSAPP_VERIFY_TOKEN="meatyhamhock"):  # noqa: S106
        yield


@pytest.fixture
def valid_verify_request(rf: RequestFactory) -> HttpRequest:
    """A valid verify request."""
    return rf.get(
        "/",
        query_params={
            "hub.mode": "subscribe",
            "hub.challenge": "1158201444",
            "hub.verify_token": "meatyhamhock",
        },
    )
