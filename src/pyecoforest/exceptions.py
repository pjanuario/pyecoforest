import json

import httpx

ENDPOINT_PROBE_EXCEPTIONS = (json.JSONDecodeError, httpx.HTTPError)


class EcoforestError(Exception):
    """Base class for Ecoforest exceptions."""


class EcoforestAuthenticationRequired(EcoforestError):
    """Exception raised when authentication failed."""

    def __init__(self, status: str) -> None:
        self.status = status
