from http import HTTPStatus
from unittest import mock

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest, HttpResponse
from django.test.client import RequestFactory

from django_whatsapp.views import WebhookView


class TestWebhookView:
    def test_get_valid_request(self, valid_verify_request: HttpRequest) -> None:
        """Test view with valid request."""
        view = WebhookView()

        got: HttpResponse = view.get(valid_verify_request)

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.OK
        assert got.content == b"1158201444"

    def test_get_invalid_request(self, rf: RequestFactory) -> None:
        """Test view with valid request."""
        view = WebhookView()
        request: HttpRequest = rf.get(
            "/",
            query_params={
                "hub.mode": "verify",
                "hub.challenge": "1158201444",
                "hub.verify_token": "meatyhamhock",
            },
        )

        with mock.patch("django_whatsapp.views.verify_request", side_effect=SuspiciousOperation) as mock_verify_request:
            got: HttpResponse = view.get(request)

        assert isinstance(got, HttpResponse)
        assert got.status_code == HTTPStatus.BAD_REQUEST
        mock_verify_request.assert_called_once_with(request, verify_token=settings.WHATSAPP_VERIFY_TOKEN)
