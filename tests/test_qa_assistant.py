import os
import pytest

from dotenv import load_dotenv

load_dotenv()
api_key = False if os.getenv("LLAMACLOUD_API_KEY") is not None else True
extract_agent_id = False if os.getenv("EXTRACT_AGENT_ID") is not None else True
env_vars_not_available = api_key and extract_agent_id


@pytest.mark.skipif(
    condition=env_vars_not_available,
    reason="No API key or extract agent ID available",
)
def test_assistant() -> None:
    from src.mcp_on_the_flight.utils import assistant_index

    response = assistant_index(
        question="What are the cancellation policies for Delta Airlines?"
    )
    assert isinstance(response, str)
