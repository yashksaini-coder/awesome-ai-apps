"""
Lesson 4: Integrating External Tools with MCP

This script demonstrates how to dynamically grant an agent new capabilities
by connecting it to an external tool server using the Multi-Capability
Protocol (MCP).

We will connect to a public MCP server that provides tools for searching
the official AWS documentation, allowing our agent to answer questions
about AWS services with up-to-date information.

Key Features:
- Dynamic tool discovery from external MCP servers
- Real-time AWS documentation access
- Seamless integration with Strands agents
- No code changes required when tools are updated on the server
"""

import os
from dotenv import load_dotenv
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models.litellm import LiteLLMModel
from strands.tools.mcp import MCPClient

# Load environment variables from a .env file
load_dotenv()


def create_aws_doc_agent() -> Agent:
    """
    Creates an agent that can query the AWS documentation via an MCP server.

    This function sets up a complete MCP-powered agent by:
    1. Configuring a language model (DeepSeek V3)
    2. Connecting to the AWS documentation MCP server
    3. Dynamically discovering available tools
    4. Creating an agent with AWS expertise

    Returns:
        Agent: An Agent instance equipped with tools from the AWS documentation MCP server.

    Raises:
        ValueError: If the NEBIUS_API_KEY environment variable is not set.
        ConnectionError: If unable to connect to the MCP server.
    """
    # Validate required environment variables
    nebius_api_key = os.getenv("NEBIUS_API_KEY")
    if not nebius_api_key:
        raise ValueError("NEBIUS_API_KEY environment variable is required")

    # Configure the language model with DeepSeek V3
    model = LiteLLMModel(
        client_args={"api_key": nebius_api_key},
        model_id="nebius/deepseek-ai/DeepSeek-V3-0324",
    )

    # Set up the MCP client to connect to the AWS documentation server.
    # This uses `uvx` to run the server package on-the-fly without installation.
    # The server provides tools for searching and retrieving AWS documentation.
    mcp_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
            )
        )
    )

    # The 'with' statement manages the lifecycle of the MCP server process.
    # It ensures proper connection, tool discovery, and cleanup.
    with mcp_client:
        # Fetch the list of available tools from the running MCP server.
        # This is where the magic happens - tools are discovered dynamically!
        aws_tools = mcp_client.list_tools_sync()
        print(f"Successfully loaded {len(aws_tools)} tools from the MCP server.")

        # Create the agent and provide it with the dynamically loaded tools.
        # The agent will now have access to real-time AWS documentation.
        aws_doc_agent = Agent(
            model=model,
            tools=aws_tools,
            system_prompt=(
                "You are an expert on Amazon Web Services. "
                "Use the provided tools to answer questions about AWS services "
                "based on the official documentation. Always provide accurate, "
                "up-to-date information from the AWS docs."
            ),
        )
        return aws_doc_agent


def main():
    """
    Main function to demonstrate using an MCP-powered agent.

    This function showcases the power of MCP by:
    1. Creating an agent with AWS documentation tools
    2. Asking a specific AWS question
    3. Demonstrating how the agent uses external tools to provide accurate answers

    The agent will automatically use the appropriate AWS documentation tools
    to find the most current and accurate information.
    """
    try:
        # Create the agent with AWS documentation capabilities
        print("Creating AWS documentation agent...")
        agent = create_aws_doc_agent()

        # Define a user query about an AWS service
        user_query = "What is the maximum invocation payload size for AWS Lambda?"

        print("\n--- Querying AWS Documentation ---")
        print(f"User Query: {user_query}\n")

        # Invoke the agent. It will use the tools from the MCP server to find the answer.
        # The agent will automatically decide which tools to use based on the query.
        response = agent(user_query)

        print("--- Agent Response ---")
        print(response)

    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please ensure NEBIUS_API_KEY is set in your environment.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
