import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from llama_cloud_services import LlamaExtract
from src.mcp_on_the_flight.models import PlaneTicket


def main() -> int:
    load_dotenv()
    conn = LlamaExtract(api_key=os.getenv("LLAMACLOUD_API_KEY"))
    agent = conn.create_agent(
        name="plane-ticket-extract-agent", data_schema=PlaneTicket
    )
    with open(".env", "a") as f:
        f.write(f'\nEXTRACT_AGENT_ID="{agent.id}"')
    return 0


if __name__ == "__main__":
    main()
