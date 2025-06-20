"""MCP server."""

import os
from dotenv import load_dotenv
import asyncio

from fastmcp import FastMCP
from utils import (
    extract_ticket_info,
    read_companies_resource,
    search_for_company_policies,
)
from models import CompanyPolicies
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage

load_dotenv()

mcp = FastMCP("MCP On The Flight")
llm = OpenAI(model="gpt-4.1", api_key=os.getenv("OPENAI_API_KEY"))
llm_struct = llm.as_structured_llm(CompanyPolicies)


@mcp.tool(
    name="extract_ticket_info", description="Extract information from a plane ticket"
)
async def extract_ticket_info_tool(plane_ticket: os.PathLike[str]) -> str:
    plane_ticket = str(plane_ticket)
    response = await asyncio.wait_for(
        extract_ticket_info(plane_ticket=plane_ticket),
        timeout=200,
    )
    await asyncio.sleep(1)
    return response


@mcp.tool(
    name="search_for_company_policies",
    description="Search for the policies of a company",
)
async def search_for_company_policies_tool(company: str) -> str:
    companies = await read_companies_resource()
    if company not in companies["companies"]:
        await search_for_company_policies(company=company)
        with open("data/last_researched_company.md") as f:
            content = f.read()
        messages = [
            ChatMessage(role="assistant", content=content),
            ChatMessage(
                role="user", content="Can you summarize these policies for me?"
            ),
        ]
        resp = await llm_struct.achat(messages)
        return resp.message.blocks[0].text
    else:
        return f"The policies for {company} are already in our database, you can directly refer any question to out Q&A assistant!"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
