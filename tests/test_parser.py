from pyecoforest.models.state import State
from pyecoforest.models.status import Status
from pyecoforest.parser import parse


def test_parser():
    response = "on_off=0\nestado=0\nconsigna_potencia=5\ntemperatura=21.5\n"
    assert parse(response) == Status(False, State.OFF, 5, 21.5)
