"""
Multiple MCP Servers Integration Example

This script demonstrates how to connect an agent to multiple MCP servers
simultaneously, combining their tools to create a more powerful agent.

In this example, we connect to:
1. Exa AI Search MCP server - for web search capabilities
2. Airbnb MCP server - for accommodation search capabilities

The agent can then use tools from both servers to answer complex queries
that require both web search and accommodation data.
"""

from mcp import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from strands import Agent
from strands.models.litellm import LiteLLMModel
from strands.tools.mcp import MCPClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_multi_mcp_agent() -> Agent:
    """
    Creates an agent with tools from multiple MCP servers.

    This function demonstrates how to combine tools from different MCP servers
    to create a more capable agent. The agent will have access to:
    - Web search capabilities (via Exa AI)
    - Accommodation search capabilities (via Airbnb)

    Returns:
        Agent: An agent equipped with tools from multiple MCP servers.

    Raises:
        ValueError: If required API keys are not set.
        ConnectionError: If unable to connect to any MCP server.
    """
    # Validate required environment variables
    nebius_api_key = os.getenv("NEBIUS_API_KEY")
    exa_api_key = os.getenv("EXA_API_KEY")

    if not nebius_api_key:
        raise ValueError("NEBIUS_API_KEY environment variable is required")
    if not exa_api_key:
        raise ValueError("EXA_API_KEY environment variable is required")

    # Configure the language model
    model = LiteLLMModel(
        client_args={"api_key": nebius_api_key},
        model_id="nebius/deepseek-ai/DeepSeek-V3-0324",
    )

    # Set up the Exa AI web search MCP client
    # This provides intelligent web search capabilities
    web_search_mcp_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=["-y", "mcp-remote", "https://mcp.exa.ai/mcp"],
                env={
                    "EXA_API_KEY": exa_api_key,
                },
            )
        )
    )

    # Set up the Airbnb MCP client
    # This provides accommodation search and booking capabilities
    airbnb_mcp_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            )
        )
    )

    # Use both servers together
    with web_search_mcp_client, airbnb_mcp_client:
        # Combine tools from both servers
        web_search_tools = web_search_mcp_client.list_tools_sync()
        airbnb_tools = airbnb_mcp_client.list_tools_sync()
        all_tools = web_search_tools + airbnb_tools

        print(f"Loaded {len(web_search_tools)} web search tools")
        print(f"Loaded {len(airbnb_tools)} Airbnb tools")
        print(f"Total tools available: {len(all_tools)}")

        # Create an agent with all tools from both servers
        agent = Agent(
            tools=all_tools,
            model=model,
            system_prompt=(
                "You are a helpful travel assistant with access to both web search "
                "and accommodation search capabilities. Use the appropriate tools "
                "to help users find information and plan their travels."
            ),
        )
        return agent


def main():
    """
    Main function demonstrating multi-MCP server integration.

    This function showcases how an agent can leverage multiple external
    tool servers to provide comprehensive answers to complex queries.
    """
    try:
        # Create the multi-MCP agent
        print("Creating multi-MCP agent...")
        agent = create_multi_mcp_agent()

        # Example queries that benefit from multiple tool sources
        example_queries = [
            "What's the fastest way to get to Barcelona from London?",
            "What listings are available in Cape Town for 2 people for 3 nights from 1 to 4 November 2025?",
        ]

        # Use the first query for demonstration
        prompt = example_queries[0]

        print(f"\n--- Querying with Multiple MCP Servers ---")
        print(f"User Query: {prompt}\n")

        # The agent will automatically use the appropriate tools
        # from both servers to provide a comprehensive answer
        response = agent(prompt)

        print("--- Agent Response ---")
        print(response)

    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please ensure all required API keys are set in your environment.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
