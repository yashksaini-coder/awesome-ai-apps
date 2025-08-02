# from agno.models.openai import OpenAIChat
import asyncio
from agno.models.nebius import Nebius
from agno.tools.mcp import MCPTools
from typing import AsyncIterator
from agno.agent import Agent, RunResponseEvent
from agno.utils.pprint import pprint_run_response
import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

server_url = "https://mintlify.com/docs/mcp"

async def run_mcp_agent(url: str, query: str):

    print("Starting MCP Agent with URL:", url)
    # Initialize the MCP tools
    mcp_tools = MCPTools(url=url, transport="streamable-http")

    # Connect to the MCP server
    await mcp_tools.connect()

    # Initialize the Agent
    agent = Agent(
        model=Nebius(
            id="deepseek-ai/DeepSeek-V3-0324",
            api_key=os.getenv("NEBIUS_API_KEY")
        ),
        tools=[mcp_tools]
    )

    # Run the agent
    # await agent.aprint_response("How to migrate documentation from your current platform to Mintlify?", stream=True)

    response = await agent.arun(query)

    print("Response received from the agent")
    # print(response)

    # Close the MCP connection
    await mcp_tools.close()

    return response.content

# Streamlit app configuration
st.set_page_config(page_title="Talk to Your Docs", page_icon="📚", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns([4, 1])
with col1:
    # Create title with embedded images
    title_html = f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <h1 style="margin: 0;">
             📚 Talk to Your Docs
            </h1>
        </div>
        """
    st.markdown(title_html, unsafe_allow_html=True)

with col2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

with st.sidebar:
    # Try to load the Nebius logo, use a fallback if not found
    try:
        st.image("./assets/Nebius.png", width=150)
    except:
        st.markdown("### 🤖 Nebius AI")

    # Model selection
    nebius_api_key = st.text_input(
        "Nebius API Key",
        value=os.getenv("NEBIUS_API_KEY", ""),
        type="password",
        help="Your Nebius API key",
    )

    st.divider()
    
    # Documentation URL input
    doc_url = st.text_input(
        "Documentation URL",
        value=server_url,
        help="Enter the URL of the documentation you want to query",
    )
    
    st.divider()
    
    # Example questions
    st.markdown("### 💡 Example Questions")
    example_questions = [
        "How to migrate documentation from your current platform to Mintlify?",
        "What are the key features of the documentation platform?",
        "How do I set up authentication?",
        "What are the best practices for documentation?",
    ]
    
    for question in example_questions:
        if st.button(question, key=f"example_{hash(question)}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()

# Main chat interface
# st.markdown("### 💬 Chat with Documentation")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask a question about the documentation...")

# Check if we have a new message that hasn't been processed yet
if st.session_state.messages and len(st.session_state.messages) > 0:
    last_message = st.session_state.messages[-1]
    if last_message["role"] == "user":
        # Check if this user message has already been responded to
        if len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] != "assistant":
            prompt = last_message["content"]

if prompt:
    # Check if API key is provided
    if not nebius_api_key:
        st.error("Please enter your Nebius API key in the sidebar.")
        st.stop()
    
    # Add user message to chat history only if it's from chat input (not from example button)
    if not (st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.messages[-1]["content"] == prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                # Update environment variable for this session
                os.environ["NEBIUS_API_KEY"] = nebius_api_key
                
                # Run the MCP agent
                response_text = asyncio.run(run_mcp_agent(doc_url, prompt))
            
            # Display the response after spinner is done
            if response_text:
                st.markdown(response_text)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                error_message = "No response received from the agent."
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})


# if __name__ == "__main__":
#     # This section is only for testing the MCP agent directly
#     # The Streamlit app runs the agent through the UI above
#     pass

    