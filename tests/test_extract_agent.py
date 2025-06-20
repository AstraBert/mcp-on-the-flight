import pytest
import os
import json

from json import JSONDecodeError
from dotenv import load_dotenv
from typing import Callable, Tuple, Union
from pydantic_core import ValidationError
from src.mcp_on_the_flight.models import PlaneTicket

load_dotenv()
api_key = False if os.getenv("LLAMACLOUD_API_KEY") is not None else True
extract_agent_id = False if os.getenv("EXTRACT_AGENT_ID") is not None else True
env_vars_not_available = api_key and extract_agent_id


@pytest.fixture()
def is_serializable_fn() -> Callable[[str], Tuple[bool, Union[None, dict]]]:
    def is_serialazable(s: str) -> bool:
        try:
            d = json.loads(s)
            return True, d
        except JSONDecodeError:
            return False, None

    return is_serialazable


@pytest.fixture()
def plane_ticket_path() -> str:
    return "data/tests/boarding-pass.pdf"


@pytest.mark.skipif(
    condition=env_vars_not_available,
    reason="No API key or extract agent ID available",
)
@pytest.mark.asyncio
async def test_extract_agent(
    is_serializable_fn: Callable, plane_ticket_path: str
) -> None:
    from src.mcp_on_the_flight.utils import extract_ticket_info

    result = await extract_ticket_info(plane_ticket=plane_ticket_path)
    assert isinstance(result, str)
    serializable, serialized = is_serializable_fn(result)
    assert serializable
    assert isinstance(serialized, dict)
    try:
        PlaneTicket.model_validate(serialized)
        model_validated = True
    except ValidationError:
        model_validated = False
    assert model_validated
