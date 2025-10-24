from http import HTTPStatus
from unittest import mock

import pytest
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.test.client import AsyncRequestFactory, RequestFactory

from django_whatsapp.views import WebhookView


class SyncWebhookView(WebhookView):
    def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse()


class AsyncWebhookView(WebhookView):
    async def post(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse()


class TestWebhookView:
    def test_get_valid_request(self, valid_verify_request: WSGIRequest) -> None:
        """Test view with valid request."""
        view = SyncWebhookView.as_view()

        got: HttpResponseBase = view(valid_verify_request)

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.OK
        assert got.content == b"1158201444"

    def test_get_invalid_request(self, rf: RequestFactory) -> None:
        """Test view with valid request."""
        view = SyncWebhookView.as_view()
        request: WSGIRequest = rf.get(
            "/",
            query_params={
                "hub.mode": "verify",
                "hub.challenge": "1158201444",
                "hub.verify_token": "meatyhamhock",
            },
        )

        with mock.patch("django_whatsapp.views.verify_request", side_effect=SuspiciousOperation) as mock_verify_request:
            got: HttpResponseBase = view(request)

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.BAD_REQUEST
        mock_verify_request.assert_called_once_with(request, verify_token=settings.WHATSAPP_VERIFY_TOKEN)

    @pytest.mark.asyncio
    async def test_get_valid_request_async(self, avalid_verify_request: ASGIRequest) -> None:
        """Test view with valid request."""
        view = AsyncWebhookView.as_view()

        got: HttpResponseBase = await view(avalid_verify_request)  # type: ignore[misc]

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.OK
        assert got.content == b"1158201444"

    @pytest.mark.asyncio
    async def test_get_invalid_request_async(self, async_rf: AsyncRequestFactory) -> None:
        """Test view with valid request."""
        view = AsyncWebhookView.as_view()
        request: ASGIRequest = async_rf.get(
            "/",
            query_params={
                "hub.mode": "verify",
                "hub.challenge": "1158201444",
                "hub.verify_token": "meatyhamhock",
            },
        )

        with mock.patch("django_whatsapp.views.verify_request", side_effect=SuspiciousOperation) as mock_verify_request:
            got: HttpResponse = await view(request)  # type: ignore[misc]

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.BAD_REQUEST
        mock_verify_request.assert_called_once_with(request, verify_token=settings.WHATSAPP_VERIFY_TOKEN)

    def test_post_invalid_signature(self, rf: RequestFactory) -> None:
        """Test POST request with invalid signature."""
        view = SyncWebhookView.as_view()
        request: WSGIRequest = rf.post("/")

        with mock.patch(
            "django_whatsapp.mixins.verify_signature", side_effect=SuspiciousOperation
        ) as mock_verify_signature:
            got: HttpResponseBase = view(request)

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.BAD_REQUEST
        mock_verify_signature.assert_called_once_with(request, app_secret=settings.WHATSAPP_APP_SECRET)

    def test_post_valid_signature(self, rf: RequestFactory) -> None:
        """Test POST request with valid signature."""
        view = SyncWebhookView.as_view()
        request: WSGIRequest = rf.post("/")

        with mock.patch("django_whatsapp.mixins.verify_signature") as mock_verify_signature:
            got: HttpResponseBase = view(request)

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.OK
        mock_verify_signature.assert_called_once_with(request, app_secret=settings.WHATSAPP_APP_SECRET)

    @pytest.mark.asyncio
    async def test_post_invalid_signature_async(self, async_rf: AsyncRequestFactory) -> None:
        """Test POST request with invalid signature."""
        view = AsyncWebhookView.as_view()
        request: ASGIRequest = async_rf.post("/")

        with mock.patch(
            "django_whatsapp.mixins.verify_signature", side_effect=SuspiciousOperation
        ) as mock_verify_signature:
            got: HttpResponseBase = await view(request)  # type: ignore[misc]

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.BAD_REQUEST
        mock_verify_signature.assert_called_once_with(request, app_secret=settings.WHATSAPP_APP_SECRET)

    @pytest.mark.asyncio
    async def test_post_valid_signature_async(self, async_rf: AsyncRequestFactory) -> None:
        """Test POST request with valid signature."""
        view = AsyncWebhookView.as_view()
        request: ASGIRequest = async_rf.post("/")

        with mock.patch("django_whatsapp.mixins.verify_signature") as mock_verify_signature:
            got: HttpResponseBase = await view(request)  # type: ignore[misc]

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.OK
        mock_verify_signature.assert_called_once_with(request, app_secret=settings.WHATSAPP_APP_SECRET)
