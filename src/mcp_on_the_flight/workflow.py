import json

from typing import Annotated
from workflows import Workflow, step
from workflows.context import Context
from workflows.events import Event, StartEvent, StopEvent
from workflows.resource import Resource
from llama_index.tools.mcp import BasicMCPClient
from models import PlaneTicket, CompanyPolicies

MCP_CLIENT = BasicMCPClient(command_or_url="http://localhost:8000/mcp")


def get_mcp_client(*args, **kwargs) -> BasicMCPClient:
    return MCP_CLIENT


class PlaneTicketEvent(StartEvent):
    plane_ticket: str


class PlaneTicketExtractedEvent(Event, PlaneTicket):
    pass


class CompanyPoliciesEvent(Event, CompanyPolicies):
    pass


class PlaneTicketWorkflow(Workflow):
    @step
    async def first_step(
        self,
        ev: PlaneTicketEvent,
        mcp_client: Annotated[BasicMCPClient, Resource(get_mcp_client)],
        ctx: Context,
    ) -> PlaneTicketExtractedEvent:
        ctx.write_event_to_stream(ev)
        result = await mcp_client.call_tool(
            tool_name="extract_ticket_info",
            arguments={"plane_ticket": ev.plane_ticket},
        )
        plane_ticket_info = result.content[0].text
        data = json.loads(plane_ticket_info)
        return PlaneTicketExtractedEvent.model_validate(data)

    @step
    async def second_step(
        self,
        ev: PlaneTicketExtractedEvent,
        mcp_client: Annotated[BasicMCPClient, Resource(get_mcp_client)],
        ctx: Context,
    ) -> StopEvent:
        ctx.write_event_to_stream(ev)
        result = await mcp_client.call_tool(
            tool_name="search_for_company_policies",
            arguments={"company": ev.operated_by},
        )
        company_policies = result.content[0].text
        if company_policies.startswith("The policies for"):
            return StopEvent(result=company_policies)
        else:
            data = json.loads(company_policies)
            ev1 = CompanyPoliciesEvent.model_validate(data)
            ctx.write_event_to_stream(ev1)
            return StopEvent(
                result="You can now proceed to the Q&A Assistant for any other doubt"
            )


workflow = PlaneTicketWorkflow()
