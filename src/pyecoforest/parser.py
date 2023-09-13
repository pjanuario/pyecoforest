from pyecoforest.exceptions import EcoforestError
from pyecoforest.models.state import State
from pyecoforest.models.status import Status


def parse(response: str) -> Status:
    """Parse request data and return as status model."""
    data = _parse_text(response)
    return Status(
        on=data["on_off"] == "1",
        state=_parse_state(data["estado"]),
        power=int(data["consigna_potencia"]),
        temperature=float(data["temperatura"]),
    )


def _parse_text(response: str) -> dict[str, str]:
    """Parse request data and return as dictionary."""
    # discard last line ?
    reply = dict(e.split("=") for e in response.split("\n")[:-1])
    # Remove all white spaces from bad response from ecoforest ...
    reply = {x.translate({32: None}): y for x, y in reply.items()}
    return reply


def _parse_state(state: str) -> State:
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
        if state in v:
            return State(k)

    raise EcoforestError(f"The state {state} is not a valid state!")
