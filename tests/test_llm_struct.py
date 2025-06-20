import os
import pytest

from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from src.mcp_on_the_flight.models import CompanyPolicies
import json
from json import JSONDecodeError
from typing import Callable, Tuple, Union
from pydantic_core import ValidationError

load_dotenv()
api_key = False if os.getenv("LLAMACLOUD_API_KEY") is not None else True
extract_agent_id = False if os.getenv("EXTRACT_AGENT_ID") is not None else True
openai_api_key = False if os.getenv("OPENAI_API_KEY") is not None else True
env_vars_not_available = api_key and extract_agent_id and openai_api_key


@pytest.fixture()
def is_serializable_fn() -> Callable[[str], Tuple[bool, Union[None, dict]]]:
    def is_serialazable(s: str) -> bool:
        try:
            d = json.loads(s)
            return True, d
        except JSONDecodeError:
            return False, None

    return is_serialazable


@pytest.mark.skipif(
    condition=env_vars_not_available,
    reason="No API key or extract agent ID available",
)
@pytest.mark.asyncio
async def test_llm_struct(is_serializable_fn: Callable):
    llm = OpenAI(model="gpt-4.1")
    llm_struct = llm.as_structured_llm(CompanyPolicies)
    from pathlib import Path

    if Path("data/last_researched_company.md").is_file():
        with open("data/last_researched_company.md") as f:
            content = f.read()
        messages = [
            ChatMessage(role="assistant", content=content),
            ChatMessage(
                role="user", content="Can you summarize these policies for me?"
            ),
        ]
        resp = await llm_struct.achat(messages)
        assert isinstance(resp.message.content, str)
        serializable, serialized = is_serializable_fn(resp.message.content)
        assert serializable
        assert isinstance(serialized, dict)
        try:
            CompanyPolicies.model_validate(serialized)
            no_error = True
        except ValidationError:
            no_error = False
        assert no_error
    else:
        from src.mcp_on_the_flight.utils import (
            search_for_company_policies,
            read_companies_resource,
        )

        await search_for_company_policies(company="Air France")
        data = await read_companies_resource()
        dirlist = os.listdir("data")
        assert "last_researched_company.md" in dirlist
        data["companies"].pop()
        with open("data/resources/companies.json", "w") as f:
            json.dump(data, f)
        with open("data/last_researched_company.md") as f:
            content = f.read()
        messages = [
            ChatMessage(role="assistant", content=content),
            ChatMessage(
                role="user", content="Can you summarize these policies for me?"
            ),
        ]
        resp = await llm_struct.achat(messages)
        assert isinstance(resp.message.content, str)
        serializable, serialized = is_serializable_fn(resp.message.content)
        assert serializable
        assert isinstance(serialized, dict)
        try:
            CompanyPolicies.model_validate(serialized)
            no_error = True
        except ValidationError:
            no_error = False
        assert no_error
