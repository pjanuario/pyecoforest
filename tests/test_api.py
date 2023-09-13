import logging
from pathlib import Path

import pytest
import respx
from httpx import Response

from pyecoforest.api import EcoforestApi
from pyecoforest.const import API_STATUS_OP, URL_CGI
from pyecoforest.models.state import State
from pyecoforest.models.status import Status

LOGGER = logging.getLogger(__name__)


def _fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> str:
    with open(_fixtures_dir() / name) as read_in:
        return read_in.read()


def _get_target() -> EcoforestApi:
    """Return a mock Envoy."""
    return EcoforestApi("http://127.0.0.1")


@pytest.mark.asyncio
@respx.mock
async def test_status():
    """Get status information."""
    target = _get_target()
    respx.post(path=URL_CGI, data={"idOperacion": API_STATUS_OP}).mock(
        return_value=Response(200, text=_load_fixture("op-1002.txt"))
    )
    actual = await target.status()
    assert actual is not None
    assert actual == Status(False, State.OFF, 3, 23.5)
