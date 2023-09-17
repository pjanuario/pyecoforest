import logging
from http import HTTPStatus
from typing import Any

import httpx

from pyecoforest.models.device import Device

from .const import (
    API_ALARMS_OP,
    API_SET_POWER_OP,
    API_SET_STATE_OP,
    API_SET_TEMP_OP,
    API_STATS_OP,
    API_STATUS_OP,
    LOCAL_TIMEOUT,
    URL_CGI,
)
from .exceptions import EcoforestAuthenticationRequired
from .ssl import NO_VERIFY_SSL_CONTEXT

_LOGGER = logging.getLogger(__name__)


class EcoforestApi:
    """Class for communicating with an ecoforest device."""

    def __init__(
        self,
        host: str,
        auth: httpx.BasicAuth | None = None,
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

    async def get(self) -> Device:
        """Retrieve ecoforest information from api."""
        return Device.build(
            {
                "status": await self._status(),
                "stats": await self._stats(),
                "alarms": await self._alarms(),
            }
        )

    async def turn(self, on: bool | None = False) -> Device:
        """Turn device on and off."""
        await self._request(
            data={"idOperacion": API_SET_STATE_OP, "on_off": 1 if on else 0}
        )
        return await self.get()

    async def set_temperature(self, target: float) -> Device:
        """Set device target temperature."""
        await self._request(
            data={"idOperacion": API_SET_TEMP_OP, "temperatura": target}
        )
        return await self.get()

    async def set_power(self, target: int) -> Device:
        """Set device target power."""
        await self._request(data={"idOperacion": API_SET_POWER_OP, "potencia": target})
        return await self.get()

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

        parsed = self._parse(response.text)

        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug("Received from POST with data %s", parsed)

        return parsed

    async def _status(self) -> dict[str, str]:
        """Retrieve ecoforest status."""
        return await self._request(data={"idOperacion": API_STATUS_OP})

    async def _stats(self) -> dict[str, str]:
        """Retrieve ecoforest stats."""
        return await self._request(data={"idOperacion": API_STATS_OP})

    async def _alarms(self) -> dict[str, str]:
        """Retrieve ecoforest information from api."""
        return await self._request(
            data={
                "idOperacion": API_ALARMS_OP,
            }
        )

    def _parse(self, response: str) -> dict[str, str]:
        """Parse request data and return as dictionary."""
        # discard last line ?
        reply = {}
        for e in response.split("\n")[:-1]:
            pair = e.split("=")
            # discard lines without pairs
            if len(pair) == 2:
                reply[pair[0]] = pair[1]
        # Remove all white spaces from bad response from ecoforest ...
        reply = {x.translate({32: None}): y for x, y in reply.items()}
        return reply
