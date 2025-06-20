import os
from dotenv import load_dotenv

from llama_cloud import (
    PipelineCreateEmbeddingConfig_OpenaiEmbedding,
    PipelineTransformConfig_Advanced,
    AdvancedModeTransformConfigChunkingConfig_Sentence,
    AdvancedModeTransformConfigSegmentationConfig_Page,
    PipelineCreate,
)
from llama_cloud.client import LlamaCloud
from llama_index.embeddings.openai import OpenAIEmbedding


def main():
    load_dotenv()

    embed_model = OpenAIEmbedding(
        model="text-embedding-3-large", api_key=os.getenv("OPENAI_API_KEY")
    )

    client = LlamaCloud(token=os.getenv("LLAMACLOUD_API_KEY"))

    with open("data/index/ryanair_policies.pdf", "rb") as f:
        file = client.files.upload_file(upload_file=f)

    embedding_config = PipelineCreateEmbeddingConfig_OpenaiEmbedding(
        type="OPENAI_EMBEDDING",
        component=embed_model,
    )

    segm_config = AdvancedModeTransformConfigSegmentationConfig_Page(mode="page")
    chunk_config = AdvancedModeTransformConfigChunkingConfig_Sentence(
        chunk_size=1024,
        chunk_overlap=200,
        separator="<whitespace>",
        paragraph_separator="\n\n\n",
        mode="sentence",
    )

    transform_config = PipelineTransformConfig_Advanced(
        segmentation_config=segm_config,
        chunking_config=chunk_config,
        mode="advanced",
    )

    pipeline_request = PipelineCreate(
        name="mcp_on_the_flight_pipeline",
        embedding_config=embedding_config,
        transform_config=transform_config,
        data_sink_id=os.getenv("DATA_SINK_ID"),
    )

    pipeline = client.pipelines.upsert_pipeline(request=pipeline_request)

    with open(".env", "a") as f:
        f.write(f'\nLLAMACLOUD_PIPELINE_ID="{pipeline.id}"')

    files = [{"file_id": file.id}]

    client.pipelines.add_files_to_pipeline_api(pipeline.id, request=files)

    return 0


if __name__ == "__main__":
    main()
