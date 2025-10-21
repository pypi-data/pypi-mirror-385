"""REST client handling, including SocketDevStream base class."""

from __future__ import annotations

from http import HTTPStatus
from typing import override

from requests.auth import HTTPBasicAuth
from singer_sdk import RESTStream


class SocketDevStream(RESTStream):
    """Socket stream class."""

    url_base = "https://api.socket.dev"

    extra_retry_statuses = (HTTPStatus.TOO_MANY_REQUESTS,)

    @property
    @override
    def authenticator(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(username=self.config["api_key"], password="")
