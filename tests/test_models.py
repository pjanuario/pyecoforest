import pytest

from pyecoforest.exceptions import EcoforestError
from pyecoforest.models.device import Alarm, Device, OperationMode, State


def get_api_data():
    return {
        "status": {
            "on_off": "0",
            "estado": "0",
            "consigna_potencia": "6",
            "consigna_temperatura": "22",
            "temperatura": "24.5",
            "modo_operacion": "0",
        },
        "stats": {
            "Me": "model-version",
            "Vs": "firmware-version",
            "Ns": "serial-number",
            "Tp": "33.5",
            "Th": "36.5",
            "Tn": "23.5",
            "Da": "002",
            "Nh": "000006826",
            "Ne": "001152",
            "Pn": "0.0",
            "Pf": "0.0",
            "Es": "0",
            "Ex": "0.0",
            "Ni": "0",
            "Co": "0.0",
        },
        "alarms": {"get_alarmas": "A099"},
    }


def test_operation_mode_build():
    assert OperationMode.build("0") == OperationMode.POWER
    assert OperationMode.build("1") == OperationMode.TEMPERATURE
    assert OperationMode.build("2") == OperationMode.EMERGENCY
    with pytest.raises(EcoforestError) as error:
        OperationMode.build("3")
    assert str(error.value) == "The operation mode 3 is not a valid operation!"


def test_state_build():
    assert State.build("0") == State.OFF
    for i in [*range(1, 5), 10]:
        assert State.build(i) == State.STARTING
    for i in range(5, 7):
        assert State.build(i) == State.PRE_HEATING
    assert State.build("7") == State.ON
    for i in [8, 11, -3]:
        assert State.build(i) == State.SHUTTING_DOWN
    assert State.build("-20") == State.STAND_BY
    assert State.build("-4") == State.ALARM
    with pytest.raises(EcoforestError) as error:
        State.build("9")
    assert str(error.value) == "The state 9 is not a valid state!"


def test_alarm_build():
    for i in ["A001", "A002"]:
        assert Alarm.build(i) == Alarm.AIR_DEPRESSION
    assert Alarm.build("A012") == Alarm.CPU_OVERHEATING
    assert Alarm.build("A099") == Alarm.PELLETS
    assert Alarm.build("N") is None
    assert Alarm.build("A100") == Alarm.UNKNOWN


def test_device_build():
    assert Device.build(get_api_data()) == Device(
        is_supported=False,
        model="model-version",
        model_name="Cordoba glass",
        firmware="firmware-version",
        serial_number="serial-number",
        operation_mode=OperationMode.POWER,
        on=False,
        state=State.OFF,
        power=6,
        temperature=22,
        alarm=Alarm.PELLETS,
        alarm_code="A099",
        environment_temperature=24.5,
        cpu_temperature=33.5,
        gas_temperature=36.5,
        ntc_temperature=23.5,
        depression=2,
        working_hours=6826,
        ignitions=1152,
        live_pulse=0.0,
        pulse_offset=0.0,
        working_state=0,
        extractor=0,
        working_level=0,
        convecto_air_flow=0.0,
    )


def test_device_build_with_supportted_device():
    data = get_api_data()
    data["stats"]["Me"] = "CC2014_v2"
    assert Device.build(data).is_supported is True
