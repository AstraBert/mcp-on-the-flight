"""Various code utilities."""

import os
import json
import uuid
from dotenv import load_dotenv
from typing import Dict, List

from llama_cloud_services import LlamaExtract
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_cloud.client import LlamaCloud
import html2text
from markdown_pdf import MarkdownPdf, Section
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from duckduckgo_search import DDGS

load_dotenv()

CONN = LlamaExtract(os.getenv("LLAMACLOUD_API_KEY"))
EXTRACT_AGENT = CONN.get_agent(id=os.getenv("EXTRACT_AGENT_ID"))
CLIENT = LlamaCloud(token=os.getenv("LLAMACLOUD_API_KEY"))
CRAWLER = BeautifulSoupCrawler()
INDEX = LlamaCloudIndex(
    index_id=os.getenv("LLAMACLOUD_PIPELINE_ID"),
    api_key=os.getenv("LLAMACLOUD_API_KEY"),
)
QE = INDEX.as_query_engine()
SEARCH_CLIENT = DDGS()


async def extract_ticket_info(plane_ticket: os.PathLike[str]) -> str:
    ticket_info = await EXTRACT_AGENT.aextract(files=plane_ticket)
    return json.dumps(ticket_info.data, indent=4)


@CRAWLER.router.default_handler
async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
    context.log.info(f"Processing {context.request.url} ...")
    html_content = context.soup.prettify()
    md_content = html2text.html2text(html_content)
    if md_content:
        with open("data/last_researched_company.md", "w") as tf:
            tf.write(md_content)
        pdf = MarkdownPdf()
        pdf.add_section(Section(toc=False, text=md_content))
        filename = f"data/index/{str(uuid.uuid4())}.pdf"
        pdf.save(filename)
        with open(filename, "rb") as f:
            file = CLIENT.files.upload_file(upload_file=f)
        files = [{"file_id": file.id}]
        CLIENT.pipelines.add_files_to_pipeline_api(
            pipeline_id=os.getenv("LLAMACLOUD_PIPELINE_ID"), request=files
        )
        context.log.info(f"Processed {context.request.url}")
    context.log.error(
        f"Failed to process {context.request.url} because it returned an empty content"
    )


async def read_companies_resource() -> Dict[str, List]:
    with open("data/resources/companies.json", "r") as f:
        data = json.load(f)
    return data


async def set_processed_companies_resource(company: str) -> None:
    data = await read_companies_resource()
    data["companies"].append(company)
    with open("data/resources/companies.json", "w") as f:
        json.dump(data, f)


async def search_for_company_policies(company: str) -> List[str]:
    results = SEARCH_CLIENT.text(keywords=f"{company} flight policies", max_results=2)
    urls_to_scrape = [r["href"] for r in results]
    await CRAWLER.run(requests=urls_to_scrape)
    await set_processed_companies_resource(company=company)
    return urls_to_scrape


def assistant_index(question: str):
    response = QE.query(question)
    return response.response
