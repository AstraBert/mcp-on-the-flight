import pytest
import os
import json

from dotenv import load_dotenv

load_dotenv()
api_key = False if os.getenv("LLAMACLOUD_API_KEY") is not None else True
extract_agent_id = False if os.getenv("EXTRACT_AGENT_ID") is not None else True
env_vars_not_available = api_key and extract_agent_id


@pytest.mark.asyncio
@pytest.mark.skipif(
    condition=env_vars_not_available,
    reason="No API key or extract agent ID available",
)
async def test_read_compansies_resource() -> None:
    from src.mcp_on_the_flight.utils import read_companies_resource

    data = await read_companies_resource()
    assert isinstance(data, dict)
    assert "companies" in data
    assert isinstance(data["companies"], list)
    assert len(data["companies"]) >= 1


@pytest.mark.asyncio
@pytest.mark.skipif(
    condition=env_vars_not_available,
    reason="No API key or extract agent ID available",
)
async def test_set_compansies_resource() -> None:
    from src.mcp_on_the_flight.utils import (
        set_processed_companies_resource,
        read_companies_resource,
    )

    await set_processed_companies_resource(company="Air France")
    data = await read_companies_resource()
    assert "Air France" in data["companies"]
    data["companies"].pop()
    with open("data/resources/companies.json", "w") as f:
        json.dump(data, f)


@pytest.mark.asyncio
@pytest.mark.skipif(
    condition=env_vars_not_available,
    reason="No API key or extract agent ID available",
)
async def test_search() -> None:
    from src.mcp_on_the_flight.utils import (
        read_companies_resource,
        search_for_company_policies,
    )
    from pathlib import Path

    if Path("data/last_researched_company.md").is_file():
        os.remove("data/last_researched_company.md")
    urls = await search_for_company_policies(company="Delta")
    assert len(urls) == 2
    data = await read_companies_resource()
    assert "Delta" in data["companies"]
    dirlist = os.listdir("data/index/")
    assert len(dirlist) >= 3
    dirlist = os.listdir("data")
    assert "last_researched_company.md" in dirlist
    data["companies"].pop()
    with open("data/resources/companies.json", "w") as f:
        json.dump(data, f)
