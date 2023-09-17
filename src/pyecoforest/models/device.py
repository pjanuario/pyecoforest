"""Model for the Ecoforest stove status."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pyecoforest.const import MODEL_NAME
from pyecoforest.exceptions import EcoforestError


class OperationMode(Enum):
    """Model that represents the device operation modes."""

    POWER = "power"
    TEMPERATURE = "temperature"
    EMERGENCY = "emergency"

    @classmethod
    def build(cls, mode: str) -> OperationMode:
        """Parse the operation mode code to an OperationMode object."""
        modes = {
            "0": OperationMode.POWER,
            "1": OperationMode.TEMPERATURE,
            "2": OperationMode.EMERGENCY,
        }

        if mode in modes:
            return modes[mode]

        raise EcoforestError(f"The operation mode {mode} is not a valid operation!")


class State(Enum):
    """Model that represents the state of the device."""

    OFF = "off"
    STARTING = "starting"
    PRE_HEATING = "pre_heating"
    ON = "on"
    SHUTTING_DOWN = "shutting_down"
    STAND_BY = "stand_by"
    ALARM = "alarm"

    @classmethod
    def build(cls, state: str) -> State:
        """Parse the state code to a State object."""
        states = {
            "OFF": [0],
            "STARTING": [1, 2, 3, 4, 10],
            "PRE_HEATING": [5, 6],
            "ON": [7],
            "SHUTTING_DOWN": [8, 11, -3],
            "STAND_BY": [-20],
            "ALARM": [-4],
        }

        for k, v in states.items():
            if int(state) in v:
                return State[k]

        raise EcoforestError(f"The state {state} is not a valid state!")


class Alarm(Enum):
    """Model that represents the alarms of the device."""

    AIR_DEPRESSION = "air_depression"
    PELLETS = "pellets"
    CPU_OVERHEATING = "cpu_overheating"
    UNKNOWN = "unknown"

    @classmethod
    def build(cls, alarm: str) -> Alarm | None:
        """Parse the alarm code to an Alarm object."""
        alarms = {
            "A001": Alarm.AIR_DEPRESSION,
            "A002": Alarm.AIR_DEPRESSION,
            "A012": Alarm.CPU_OVERHEATING,
            "A099": Alarm.PELLETS,
            "N": None,
        }

        if alarm in alarms:
            return alarms[alarm]

        return Alarm.UNKNOWN


@dataclass
class Device:
    """Model for the Ecoforest stove."""

    # model information
    firmware: str
    model: str
    model_name: str
    serial_number: str

    # confirguation information
    operation_mode: OperationMode

    # status information
    on: bool
    state: State
    power: int
    temperature: float
    alarm: Alarm | None = None
    alarm_code: str | None = None

    # sensors
    environment_temperature: float | None = None
    cpu_temperature: float | None = None
    gas_temperature: float | None = None
    ntc_temperature: float | None = None

    @classmethod
    def build(cls, data: dict[str, dict[str, str]]) -> Device:
        """Parse request data and return as Device."""
        status = data["status"]
        stats = data["stats"]
        alarms = data["alarms"]
        return Device(
            model=stats["Me"],
            model_name=MODEL_NAME,
            firmware=stats["Vs"],
            serial_number=stats["Ns"],
            operation_mode=OperationMode.build(status["modo_operacion"]),
            on=status["on_off"] == "1",
            state=State.build(status["estado"]),
            power=int(status["consigna_potencia"]),
            temperature=float(status["consigna_temperatura"]),
            alarm=Alarm.build(alarms["get_alarmas"]),
            alarm_code=alarms["get_alarmas"] if alarms["get_alarmas"] != "N" else None,
            environment_temperature=float(status["temperatura"]),
            cpu_temperature=float(stats["Tp"]),
            gas_temperature=float(stats["Th"]),
            ntc_temperature=float(stats["Tn"]),
        )
