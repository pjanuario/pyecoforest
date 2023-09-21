from pathlib import Path

import httpx
import pytest
import respx

from pyecoforest.api import EcoforestApi
from pyecoforest.const import (
    API_ALARMS_OP,
    API_SET_POWER_OP,
    API_SET_STATE_OP,
    API_SET_TEMP_OP,
    API_STATS_OP,
    API_STATUS_OP,
    URL_CGI,
)
from pyecoforest.exceptions import (
    EcoforestAuthenticationRequired,
    EcoforestConnectionError,
)
from pyecoforest.models.device import Device, OperationMode, State


def _fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> str:
    with open(_fixtures_dir() / name) as read_in:
        return read_in.read()


def _mutate_fixture(name: str, pairs: list[tuple[str, str]]) -> str:
    fixture = _load_fixture(name)
    for k, v in pairs:
        fixture = fixture.replace(k, v)
    return fixture


def _get_target() -> EcoforestApi:
    """Return a mock Envoy."""
    return EcoforestApi("http://127.0.0.1")


@pytest.mark.asyncio
@respx.mock
async def test_get():
    """Get status information."""
    target = _get_target()
    respx.post(path=URL_CGI, data={"idOperacion": API_STATUS_OP}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1002-status.txt"))
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_STATS_OP}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1020-stats.txt"))
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_ALARMS_OP}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1079-alarms.txt"))
    )
    actual = await target.get()
    assert actual is not None
    assert actual == Device(
        model="CC2014_v2",
        model_name="Cordoba glass",
        firmware="30Abr19_v2z",
        serial_number="000025568680000",
        operation_mode=OperationMode.POWER,
        on=False,
        state=State.OFF,
        power=3,
        temperature=20.5,
        alarm=None,
        alarm_code=None,
        environment_temperature=23.5,
        cpu_temperature=32.3,
        gas_temperature=28.1,
        ntc_temperature=25,
    )


@pytest.mark.asyncio
@respx.mock
@pytest.mark.parametrize(
    ("side_effect", "expected", "message"),
    [
        (
            httpx.Response(401),
            EcoforestAuthenticationRequired,
            "401",
        ),
        (
            httpx.TimeoutException("timeout"),
            EcoforestConnectionError,
            "Timeout occurred while connecting to the device.",
        ),
        (
            httpx.Response(500),
            EcoforestConnectionError,
            "Error occurred while communicating with device.",
        ),
    ],
)
async def test_get_errors(side_effect, expected, message):
    """Get status information with error."""
    target = _get_target()
    respx.post(path=URL_CGI, data={"idOperacion": API_STATUS_OP}).mock(
        side_effect=side_effect
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_STATS_OP}).mock(
        side_effect=side_effect
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_ALARMS_OP}).mock(
        side_effect=side_effect
    )

    with pytest.raises(expected) as err:
        await target.get()
    assert str(err.value) == message


@pytest.mark.asyncio
@respx.mock
async def test_set_temperature():
    """Set target temperature."""
    target = _get_target()
    respx.post(path=URL_CGI, data={"idOperacion": API_STATUS_OP}).mock(
        return_value=httpx.Response(
            200,
            text=_mutate_fixture(
                "op-1002-status.txt",
                [("consigna_temperatura=20.5", "consigna_temperatura=23.5")],
            ),
        )
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_STATS_OP}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1020-stats.txt"))
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_ALARMS_OP}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1079-alarms.txt"))
    )
    respx.post(
        path=URL_CGI, data={"idOperacion": API_SET_TEMP_OP, "temperatura": 23.5}
    ).mock(return_value=httpx.Response(200, text=_load_fixture("op-1019-set-temp.txt")))

    actual = await target.set_temperature(23.5)
    assert actual is not None
    assert actual == Device(
        model="CC2014_v2",
        model_name="Cordoba glass",
        firmware="30Abr19_v2z",
        serial_number="000025568680000",
        operation_mode=OperationMode.POWER,
        on=False,
        state=State.OFF,
        power=3,
        temperature=23.5,
        alarm=None,
        alarm_code=None,
        environment_temperature=23.5,
        cpu_temperature=32.3,
        gas_temperature=28.1,
        ntc_temperature=25,
    )


@pytest.mark.asyncio
@respx.mock
async def test_set_power():
    """Set target power."""
    target = _get_target()
    respx.post(path=URL_CGI, data={"idOperacion": API_STATUS_OP}).mock(
        return_value=httpx.Response(
            200,
            text=_mutate_fixture(
                "op-1002-status.txt", [("consigna_potencia=3", "consigna_potencia=5")]
            ),
        )
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_STATS_OP}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1020-stats.txt"))
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_ALARMS_OP}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1079-alarms.txt"))
    )
    respx.post(
        path=URL_CGI, data={"idOperacion": API_SET_POWER_OP, "potencia": 5}
    ).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1004-set-power.txt"))
    )

    actual = await target.set_power(5)
    assert actual is not None
    assert actual == Device(
        model="CC2014_v2",
        model_name="Cordoba glass",
        firmware="30Abr19_v2z",
        serial_number="000025568680000",
        operation_mode=OperationMode.POWER,
        on=False,
        state=State.OFF,
        power=5,
        temperature=20.5,
        alarm=None,
        alarm_code=None,
        environment_temperature=23.5,
        cpu_temperature=32.3,
        gas_temperature=28.1,
        ntc_temperature=25,
    )


@pytest.mark.asyncio
@respx.mock
async def test_turn():
    """Turn on device status."""
    target = _get_target()
    respx.post(path=URL_CGI, data={"idOperacion": API_STATUS_OP}).mock(
        return_value=httpx.Response(
            200,
            text=_mutate_fixture(
                "op-1002-status.txt",
                [("on_off=0", "on_off=1"), ("estado=0", "estado=1")],
            ),
        )
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_STATS_OP}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1020-stats.txt"))
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_ALARMS_OP}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1079-alarms.txt"))
    )
    respx.post(path=URL_CGI, data={"idOperacion": API_SET_STATE_OP, "on_off": 1}).mock(
        return_value=httpx.Response(200, text=_load_fixture("op-1004-set-power.txt"))
    )

    actual = await target.turn(True)
    assert actual is not None
    assert actual == Device(
        model="CC2014_v2",
        model_name="Cordoba glass",
        firmware="30Abr19_v2z",
        serial_number="000025568680000",
        operation_mode=OperationMode.POWER,
        on=True,
        state=State.STARTING,
        power=3,
        temperature=20.5,
        alarm=None,
        alarm_code=None,
        environment_temperature=23.5,
        cpu_temperature=32.3,
        gas_temperature=28.1,
        ntc_temperature=25,
    )
