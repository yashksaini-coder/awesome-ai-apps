# Couchbase MCP OpenAI Agents SDK Demo with Nebius 

## 1. Project Overview

This project demonstrates the integration of a Large Language Model (LLM) with a Couchbase database using the Model Context Protocol (MCP) and the OpenAI Agents SDK. It showcases how an AI agent can understand natural language queries, interact with a Couchbase instance to retrieve or manipulate data, and provide meaningful responses. This demo specifically focuses on querying a sample database `travel-sample` containing information about hotels, airports, airlines, routes, and landmarks, primarily within an `inventory` scope.

Users can ask questions like:
*   "List out the top 5 hotels by the highest aggregate rating?"
*   "Recommend me a flight and hotel from New York to San Francisco."

The project uses a Jupyter notebook (`main.ipynb`) to define and run the AI agent, which communicates with a Couchbase database via an MCP server.

## 2. Introduction to Model Context Protocol (MCP)

The Model Context Protocol (MCP) is an open standard designed to standardize how AI assistants and applications connect to and interact with external data sources, tools, and systems. Think of MCP as a universal adapter that allows AI models to seamlessly access the context they need to produce more relevant, accurate, and actionable responses.

**Key Goals and Features of MCP:**

*   **Standardized Communication:** MCP provides a common language and structure for AI models to communicate with diverse backend systems, replacing the need for numerous custom integrations.
*   **Enhanced Context Management:** It helps manage the limited context windows of LLMs efficiently, enabling them to maintain longer, more coherent interactions and leverage historical data.
*   **Secure Data Access:** MCP emphasizes secure connections, allowing developers to expose data through MCP servers while maintaining control over their infrastructure.
*   **Tool Use and Actionability:** It enables LLMs to not just retrieve information but also to use external tools and trigger actions in other systems.
*   **Interoperability:** Fosters an ecosystem where different AI tools, models, and data sources can work together more cohesively.
*   **Client-Server Architecture:** MCP typically involves:
    *   **MCP Hosts/Clients:** Applications (like AI assistants, IDEs, or other AI-powered tools) that want to access data or capabilities.
    *   **MCP Servers:** Lightweight programs that expose specific data sources or tools (e.g., a database, an API) through the standardized MCP.

MCP aims to break down data silos, making it easier for AI to integrate with real-world applications and enterprise systems, leading to more powerful and context-aware AI solutions. It is an open-source initiative, often supported by SDKs in various programming languages to facilitate the development of MCP clients and servers.

## 3. Implementation Overview

This project leverages MCP to allow an AI agent to query and understand data within a Couchbase database.

### 3.1. Core Components:

*   **`main.ipynb`:**
    *   The main Jupyter notebook that orchestrates the demonstration.
    *   It imports necessary libraries, including `agents` and `agents.mcp`.
    *   Defines the AI agent's configuration and the questions to be asked.
    *   Manages the lifecycle of the MCP server connection.
*   **`agents` library (custom/external):**
    *   Provides the `Agent` class to define the AI agent's behavior, instructions, and model (e.g., "meta-llama/Meta-Llama-3.1-8B-Instruct").
    *   Provides the `Runner` class to execute interactions with the agent.
    *   Includes `gen_trace_id` and `trace` for observability.
*   **`agents.mcp.MCPServerStdio`:**
    *   A component used to establish and manage a connection to an MCP server running as a separate process, communicating via standard input/output (stdio).
    *   In this demo, it's configured to run an external Python script (`mcp-server-couchbase/src/mcp_server.py`) which acts as the MCP server for Couchbase.
*   **`mcp-server-couchbase` (External MCP Server):**
    *   This is a separate Python application (located [here](https://github.com/Couchbase-Ecosystem/mcp-server-couchbase)) that implements the MCP server logic for Couchbase.
    *   It exposes Couchbase operations (like running SQL++ queries, fetching documents, listing scopes/collections) as tools that the AI agent can call via MCP.
    *   It requires its own environment configuration (e.g., via a `.env` file specified by the `--env-file` argument) to connect to the actual Couchbase instance.

### 3.2. Workflow:

1.  **MCP Server Initialization:**
    *   The `main.ipynb` script starts by launching the `mcp-server-couchbase` process using `MCPServerStdio`.
    *   The command to start the server is configured with the path to a `uv` executable (a Python project and virtual environment manager), the `mcp-server-couchbase` project directory, and the path to an `.env` file for its database credentials.
    *   This server listens for MCP requests from the agent.

2.  **Agent Configuration:**
    *   An `Agent` instance (named "Assistant") is created with:
        *   **System Prompt/Instructions:** Detailed instructions are provided to the LLM on how to interact with the Couchbase database. These instructions include:
            *   The hierarchical structure of Couchbase (Cluster, Bucket, Scope, Collection, Document).
            *   Specific guidance that the data of interest is within the `inventory` scope.
            *   Rules for generating SQL++ queries (e.g., only the collection name in the `FROM` clause, and enclosing all identifiers like fields, collections, scopes, or bucket names in backticks `` ` ``).
        *   **LLM Model:** Specifies the underlying language model to be used (e.g., "meta-llama/Meta-Llama-3.1-8B-Instruct").
        *   **MCP Server Connection:** The `mcp_servers` parameter links the agent to the initialized `MCPServerStdio` instance, enabling it to discover and use the Couchbase tools exposed by the MCP server.

3.  **Querying the Agent:**
    *   The `qna` asynchronous function defines a series of natural language questions.
    *   For each question, `Runner.run(starting_agent=agent, input=message)` sends the message to the "Assistant" agent.

4.  **Agent Processing and MCP Tool Use:**
    *   The agent (LLM) receives the user's question.
    *   Based on its instructions and the question, it determines if it needs to interact with the Couchbase database.
    *   If database interaction is required, the agent formulates a request to use one of the available Couchbase tools provided by the `mcp-server-couchbase` (e.g., `mcp_couchbase_run_sql_plus_plus_query`, `mcp_couchbase_get_scopes_and_collections_in_bucket`).
    *   This tool request is sent over MCP to the `mcp-server-couchbase`.
    *   The `mcp-server-couchbase` executes the requested database operation (e.g., runs a SQL++ query against the `inventory` scope).
    *   The results from the database operation are returned to the agent via MCP.

5.  **Response Generation:**
    *   The agent uses the information retrieved from Couchbase (if any) and its own reasoning capabilities to formulate a natural language response to the user's original question.
    *   The final output from the agent is then printed in the notebook.

### 3.3. Database Interaction Details:

*   **Target Database:** The agent is configured to primarily work with the `inventory` scope.
*   **Collections:** The demo implies the existence of collections such as `airport`, `airline`, `route`, `landmark`, and `hotel` within the `inventory` scope.
*   **Query Language:** The agent is instructed to generate SQL++ (N1QL) queries for Couchbase.


### 3.4. Setting Up and Running the Demo:

**Prerequisites:**

*   Python
*   Jupyter Notebook or JupyterLab.
*   Access to a running Couchbase Server instance populated with the relevant sample data (especially in the `inventory` scope with the mentioned collections).
*   The `mcp-server-couchbase` project must be available at the specified path (set as the `--directory` flag) or the path in `main.ipynb` updated accordingly.
*   A `.env` file containing the necessary Couchbase connection details for the `mcp-server-couchbase`. This file should define variables like:
    ```env
    COUCHBASE_HOST=your_couchbase_host
    COUCHBASE_BUCKET_NAME=your_bucket_name # e.g., travel-sample if that's what inventory scope is in
    COUCHBASE_USERNAME=your_couchbase_username
    COUCHBASE_PASSWORD=your_couchbase_password
    NEBIUS_API_KEY=your_nebius_api_key
    OPENAI_API_KEY=your_openai_api_key
    # Add any other variables required by mcp-server-couchbase
    ```
*   The `agents` library and its dependencies must be installed in the Python environment used by the Jupyter notebook.

**Running the Demo:**

1.  Ensure all prerequisites are met, especially the Couchbase instance and the `mcp-server-couchbase` setup.
2.  Verify that the paths in `main.ipynb` for the `uv` command, `mcp-server-couchbase` directory, and the `.env` file are correct for your environment.
3.  Open `main.ipynb` in Jupyter Notebook or JupyterLab.
4.  Run the cells in the notebook sequentially.
5.  Observe the output, which will include the questions asked and the AI agent's responses based on its interaction with the Couchbase database.
