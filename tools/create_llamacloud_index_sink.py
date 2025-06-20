import os
from dotenv import load_dotenv

from llama_cloud.types import CloudQdrantVectorStore
from llama_cloud.client import LlamaCloud

load_dotenv()


def main() -> int:
    client = LlamaCloud(token=os.getenv("LLAMACLOUD_API_KEY"))

    ds = {
        "name": "ticket-to-ride",
        "sink_type": "QDRANT",
        "component": CloudQdrantVectorStore(
            api_key=os.getenv("QDRANT_API_KEY"),
            collection_name="mcp-on-the-flight-collection",
            url=os.getenv("QDRANT_URL"),
        ),
    }
    data_sink = client.data_sinks.create_data_sink(request=ds)
    with open(".env", "a") as f:
        f.write(f'\nDATA_SINK_ID="{data_sink.id}"')
    return 0


if __name__ == "__main__":
    main()
