import os
import asyncio

import streamlit as st
from researcher import Researcher


async def run_research_agent(researcher, agent, user_input):
    """Run the research agent asynchronously"""
    try:
        response = await researcher.run_agent_with_memory(agent, user_input)
        return response
    except Exception as e:
        raise e


async def run_memory_agent(researcher, agent, user_input):
    """Run the memory agent asynchronously"""
    try:
        response = await researcher.run_agent_with_memory(agent, user_input)
        return response
    except Exception as e:
        raise e


def main():
    st.set_page_config(
        page_title="Research Agent with Memory", page_icon="🔬", layout="wide"
    )

    with open("./assets/gibson.svg", "r", encoding="utf-8") as gibson_file:
        gibson_svg = (
            gibson_file.read()
            .replace("\n", "")
            .replace("\r", "")
            .replace("  ", "")
            .replace('"', "'")
        )

    gibson_svg_inline = f'<span style="height:80px; width:200px; display:inline-block; vertical-align:middle; margin-left:8px;margin-top:20px;margin-right:8px;">{gibson_svg}</span>'

    # Create title with embedded images (SVG and PNG in one line)
    title_html = f"""
    <div style='display:flex; align-items:center; width:100%; padding:24px 0;'>
    <h1 style='margin:0; padding:0; font-size:2.5rem; font-weight:bold; display:flex; align-items:center;'>
     AI Research Assistant powered by OpenAI Agents, Tavily,  Nebius AI Studio and Memori
     {gibson_svg_inline}
    </h1>
    </div>
    """

    # st.title("")
    # st.markdown("### AI Research Assistant powered by OpenAI Agents, Memori, Tavily and Nebius AI Studio")
    st.markdown(title_html, unsafe_allow_html=True)
    st.markdown("🔬Arxiv Research Papers Agent with Persistent Memory ")

    # Sidebar with navigation and info
    with st.sidebar:
        st.header("Navigation")
        tab_choice = st.radio(
            "Choose Mode:", ["🔬 Research Chat", "🧠 Memory Chat"], key="tab_choice"
        )

        st.header("About This Demo")
        st.markdown(
            """
        This demo showcases:
        - **Research Agent**: Uses Tavily for arXiv research paper search
        - **Memori Integration**: Remembers all research sessions
        - **Memory Chat**: Query your research history

        The research agent can:
        - 🔍 Conduct comprehensive research using arXiv papers
        - 🧠 Remember all previous research 
        - 📚 Build upon past research
        - 💾 Store findings for future reference
        """
        )

        st.header("Research History")
        if st.button("📊 View All Research"):
            st.session_state.show_all_research = True

        if st.button("🗑️ Clear All Memory", type="secondary"):
            if st.session_state.get("confirm_clear_research"):
                st.success("Research memory cleared!")
                st.session_state.confirm_clear_research = False
                st.rerun()
            else:
                st.session_state.confirm_clear_research = True
                st.warning("Click again to confirm")

    # Initialize researcher
    if "researcher" not in st.session_state:
        with st.spinner("Initializing Researcher with Memory..."):
            st.session_state.researcher = Researcher()
            st.session_state.researcher.define_agents()

    # Get agents from researcher
    if "research_agent" not in st.session_state:
        st.session_state.research_agent = st.session_state.researcher.get_research_agent()

    if "memory_agent" not in st.session_state:
        st.session_state.memory_agent = st.session_state.researcher.get_memory_agent()

    # Initialize chat histories
    if "research_messages" not in st.session_state:
        st.session_state.research_messages = []
    if "memory_messages" not in st.session_state:
        st.session_state.memory_messages = []

    # Research Chat Tab
    if tab_choice == "🔬 Research Chat":
        st.header("🔬 Research Agent")
        st.markdown(
            "*Ask me to research any topic and I'll find relevant arXiv papers while remembering everything!*"
        )

        # Display research chat messages
        for message in st.session_state.research_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Research chat input
        if research_prompt := st.chat_input("What would you like me to research?"):
            # Add user message to chat history
            st.session_state.research_messages.append(
                {"role": "user", "content": research_prompt}
            )
            with st.chat_message("user"):
                st.markdown(research_prompt)

            # Generate research response
            with st.chat_message("assistant"):
                with st.spinner("🔍 Conducting research and searching memory..."):
                    try:
                        # Get response from research agent with automatic memory recording
                        response = asyncio.run(run_research_agent(
                            st.session_state.researcher,
                            st.session_state.research_agent, 
                            research_prompt
                        ))

                        # Extract response content
                        if hasattr(response, 'final_output'):
                            response_content = response.final_output
                        elif hasattr(response, 'content'):
                            response_content = response.content
                        else:
                            response_content = str(response)
                        
                        # Display the response
                        st.markdown(response_content)
                        
                        # Show confirmation that individual conversations were recorded
                        st.success("✅ All agent conversations recorded to memory!", icon="🧠")
                        
                        # Add assistant response to chat history
                        st.session_state.research_messages.append(
                            {"role": "assistant", "content": response_content}
                        )

                    except Exception as e:
                        error_message = f"Sorry, I encountered an error: {str(e)}"
                        st.error(error_message)
                        st.session_state.research_messages.append(
                            {"role": "assistant", "content": error_message}
                        )

        # Research example prompts
        if not st.session_state.research_messages:
            st.markdown("### 🔬 Example Research Topics:")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🧠 Brain-Computer Interfaces"):
                    st.session_state.research_messages.append(
                        {
                            "role": "user",
                            "content": "Research the latest developments in brain-computer interfaces",
                        }
                    )
                    st.rerun()

                if st.button("🔋 Solid-State Batteries"):
                    st.session_state.research_messages.append(
                        {
                            "role": "user",
                            "content": "Analyze the current state of solid-state batteries",
                        }
                    )
                    st.rerun()

            with col2:
                if st.button("🧬 CRISPR Gene Editing"):
                    st.session_state.research_messages.append(
                        {
                            "role": "user",
                            "content": "Research recent breakthroughs in CRISPR gene editing",
                        }
                    )
                    st.rerun()

                if st.button("🚗 Autonomous Vehicles"):
                    st.session_state.research_messages.append(
                        {
                            "role": "user",
                            "content": "Investigate the development of autonomous vehicles",
                        }
                    )
                    st.rerun()

    # Memory Chat Tab
    elif tab_choice == "🧠 Memory Chat":
        st.header("🧠 Research Memory Assistant")
        st.markdown(
            "*Ask me about your previous research sessions and I'll help you recall everything!*"
        )

        # Display memory chat messages
        for message in st.session_state.memory_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Memory chat input
        if memory_prompt := st.chat_input(
            "What would you like to know about your research history?"
        ):
            # Add user message to chat history
            st.session_state.memory_messages.append(
                {"role": "user", "content": memory_prompt}
            )
            with st.chat_message("user"):
                st.markdown(memory_prompt)

            # Generate memory response
            with st.chat_message("assistant"):
                with st.spinner("🧠 Searching through your research history..."):
                    try:
                        # Get response from memory agent with automatic memory recording
                        response = asyncio.run(run_memory_agent(
                            st.session_state.researcher,
                            st.session_state.memory_agent, 
                            memory_prompt
                        ))

                        # Extract response content
                        if hasattr(response, 'final_output'):
                            response_content = response.final_output
                        elif hasattr(response, 'content'):
                            response_content = response.content
                        else:
                            response_content = str(response)
                        
                        # Display the response
                        st.markdown(response_content)
                        
                        # Show confirmation that conversations were recorded
                        st.success("✅ Memory agent conversations recorded!", icon="🧠")
                        
                        # Add assistant response to chat history
                        st.session_state.memory_messages.append(
                            {"role": "assistant", "content": response_content}
                        )

                    except Exception as e:
                        error_message = f"Sorry, I encountered an error: {str(e)}"
                        st.error(error_message)
                        st.session_state.memory_messages.append(
                            {"role": "assistant", "content": error_message}
                        )

        # Memory example prompts
        if not st.session_state.memory_messages:
            st.markdown("### 🧠 Example Memory Queries:")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📋 What were my last research topics?"):
                    st.session_state.memory_messages.append(
                        {
                            "role": "user",
                            "content": "What were my last research topics?",
                        }
                    )
                    st.rerun()

                if st.button("🔍 Show my research on AI"):
                    st.session_state.memory_messages.append(
                        {
                            "role": "user",
                            "content": "Show me all my previous research related to artificial intelligence",
                        }
                    )
                    st.rerun()

            with col2:
                if st.button("📊 Summarize my research history"):
                    st.session_state.memory_messages.append(
                        {
                            "role": "user",
                            "content": "Can you summarize my research history and main findings?",
                        }
                    )
                    st.rerun()

                if st.button("🧬 Find my biotech research"):
                    st.session_state.memory_messages.append(
                        {
                            "role": "user",
                            "content": "Find all my research related to biotechnology and gene editing",
                        }
                    )
                    st.rerun()


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        st.error("Please set your OPENAI_API_KEY environment variable")
        st.stop()
    main()