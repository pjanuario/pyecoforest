import logging
from http import HTTPStatus
from typing import Any

import httpx

from pyecoforest.models.status import Status

from .const import API_STATUS_OP, LOCAL_TIMEOUT, URL_CGI
from .exceptions import EcoforestAuthenticationRequired
from .parser import parse
from .ssl import NO_VERIFY_SSL_CONTEXT

_LOGGER = logging.getLogger(__name__)


class EcoforestApi:
    """Class for communicating with an ecoforest device."""

    def __init__(
        self,
        host: str,
        auth: httpx.DigestAuth | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> None:
        self._host = host
        self._auth = auth
        # We use our own httpx client session so we can disable SSL verification,
        # the device use self-signed SSL certs.
        self._timeout = timeout or LOCAL_TIMEOUT
        self._client = client or httpx.AsyncClient(
            base_url=self._host, verify=NO_VERIFY_SSL_CONTEXT
        )  # nosec

    async def _request(self, data: dict[str, Any] | None = None) -> httpx.Response:
        """Make a request to the device."""
        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug("Sending POST to %s with data %s", URL_CGI, data)

        response = await self._client.post(
            URL_CGI,
            auth=self._auth,
            timeout=self._timeout,
            data=data,
        )

        status_code = response.status_code
        if status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            raise EcoforestAuthenticationRequired(
                f"Authentication failed for {URL_CGI} with status {status_code}, "
                "please check your username/password."
            )

        return parse(response.text)

    async def status(self) -> Status:
        """Retrieve ecoforest status."""
        result = await self._request(data={"idOperacion": API_STATUS_OP})
        return result
