# Database Assistant powered by Agno and GibsonAI MCP server

This project implements a conversational AI agent that acts as a GibsonAI database assistant. It can help you manage your database projects and schemas using natural language.

## Features

- **Create GibsonAI Projects**: Start new database projects from scratch.
- **Schema Management**: Define and modify tables, columns, and relationships.
- **Deploy Changes**: Apply schema changes to your hosted databases.
- **Querying**: Interact with your database schema and data.
- **Best Practices**: Get insights and recommendations on database structure.

## How It Works

The agent is built using the `agno` framework. It uses the `meta-llama/Meta-Llama-3.1-70B-Instruct` model hosted on Nebius for language understanding and generation. The `MCPTools` from the `agno` library provide a bridge to the `gibson-cli`, allowing the agent to execute commands and interact with GibsonAI.

## Getting Started

### Prerequisites

- Python 3.8+
- An account with [GibsonAI](https://gibson.ai/)
- A Nebius API key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/awesome-llm-apps.git
    cd awesome-llm-apps/mcp_ai_agents/database_mcp_agent
    ```

2.  **Set up a virtual environment and install dependencies:**
    This project uses `uv` for package management.
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt 
    ```
    *(Note: Assuming a `requirements.txt` will be created. The `pyproject.toml` is present, so `uv pip install .` might be more appropriate if the project is packaged correctly. For now, I'''ll assume a simple setup)*

3.  **Configure your environment variables:**
    Create a `.env` file in the `database_mcp_agent` directory and add your Nebius API key:
    ```
    NEBIUS_API_KEY="your_nebius_api_key"
    ```

### Usage

To run the agent, execute the `main.py` script:

```bash
python main.py
```

You can modify the `message` in the `if __name__ == "__main__":` block in `main.py` to change the initial prompt for the agent. For example:

```python
if __name__ == "__main__":
    asyncio.run(
        run_gibsonai_agent(
            '''
            Create a new GibsonAI project for my e-commerce store.
            It should have tables for products, customers, and orders.
            '''
        )
    )
```

## How to get `gibson-cli`?

To install the `gibson-cli`, you can use `uvx` or `pipx`:

```bash
uvx --from gibson-cli@latest gibson --version
```

This will download and run the Gibson CLI without installing it globally. The agent uses a similar command to interact with the MCP server.
