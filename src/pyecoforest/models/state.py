"""Model for the Ecoforest state."""

from enum import Enum


class State(Enum):
    """Model that represents the state of the device."""

    OFF = "off"
    STARTING = "starting"
    PRE_HEATING = "pre_heating"
    ON = "on"
    SHUTTING_DOWN = "shutting_down"
    STAND_BY = "stand_by"
    ALARM = "alarm"
