# server.py
import asyncio
import websockets
from workflow import (
    workflow,
    PlaneTicketEvent,
    PlaneTicketExtractedEvent,
    CompanyPoliciesEvent,
)


async def run_workflow(websocket):
    async for prompt in websocket:
        handler = workflow.run(start_event=PlaneTicketEvent(plane_ticket=prompt))
        async for event in handler.stream_events():
            if isinstance(event, PlaneTicketExtractedEvent):
                extra_info = ""
                for k, v in event.extra_information.items():
                    extra_info += f"- {k.capitalize()}: {v}\n"
                await websocket.send(
                    f"Your departure date is: **{event.depature_time}** and landing date is: **{event.landing_time}**.\n\nYour flight number (might be useful for tracking) is: *{event.flight_number}*.\n\nYou are seating at: **{event.seat_number}**.\n\nExtra information (if any):\n{extra_info}\n\n"
                )
            elif isinstance(event, CompanyPoliciesEvent):
                smoking_allowed = "" if event.smoking_allowed else "not"
                max_volume = ""
                if event.liquids.volume_limits_ml == 0:
                    max_volume = "no liquids allowed"
                elif event.liquids.volume_limits_ml == -1:
                    max_volume = "no restrictions"
                else:
                    max_volume = str(event.liquids.volume_limits_ml)
                liquids = f"- Maximum volume: {max_volume}\n- Alcoholic beverages allowed: {event.liquids.alcoholic_beverages_allowed}\n"
                policies = f"**Rules about luggage**:\n\n{event.luggage}\n\n**Forbidden items**:\n\n{event.forbidden_items}\n\n**Smoking** is {smoking_allowed} allowed.\n\n**Liquids:\n{liquids}\n\n**Rules on pharmaceuticals**:\n\n{event.pharmaceuticals}"
                await websocket.send(policies)
        response = await handler
        response = str(response)
        await websocket.send(response)
        await websocket.send("[END]")


async def main():
    print("Starting server on ws://localhost:8765")
    async with websockets.serve(run_workflow, "localhost", 8765):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
