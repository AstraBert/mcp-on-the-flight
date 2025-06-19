# MCP on the Flight!✈️

## Your Accurate Flight Assistant

> _This is just a draft :)_

This is an MCP-powered project to showcase [LlamaIndex](https://llamaindex.ai) cloud platform products.

The idea is simple, and can be represented as follows:

```mermaid
flowchart TD
    A[User] -->|Uploads their plane ticket| B(LlamaExtract)
    B -->|Ticket details| C{Flight Agent}
    C -->|Web Search| D[Company information/policies]
    C -->|Flight Radar| E[Flight status]
    E --> F(Indexing on LlamaCloud)
    D --> F
    A --> |Question| F
    F --> |Answers| A
```

### Get it up and running!

Get the GitHub repository:

```bash
git clone https://github.com/AstraBert/mcp-on-the-flight
```

Install dependencies:

```bash
uv sync
```

And then modify the `.env.example` file with your API keys and move it to `.env`.

Now you're ready to run the app:

```bash
cd src/mcp_on_the_flight
python3 main.py
```
