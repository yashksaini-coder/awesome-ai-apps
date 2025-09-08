import streamlit as st
import os
from dotenv import load_dotenv
from contextual import ContextualAI

load_dotenv()

st.set_page_config(
    page_title="Contextual AI RAG Chat",
    layout="wide"
)

if "datastore_id" not in st.session_state:
    st.session_state.datastore_id = ""
if "agent_id" not in st.session_state:
    st.session_state.agent_id = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

contextual_api_key = os.getenv("CONTEXTUAL_API_KEY")

# Initialize Contextual AI client
client = None
if contextual_api_key:
    try:
        client = ContextualAI(api_key=contextual_api_key)
    except Exception as e:
        st.error(f"Failed to initialize Contextual AI client: {e}")

# Sidebar setup w/ store, agent, and upload files
with st.sidebar:
    st.header("🤖 Contextual AI Setup")
    st.caption("Managed RAG Platform")
    
    # API Status
    st.subheader("API Status")
    if contextual_api_key and client:
        st.success("Connected")
    else:
        st.error("Not Connected")
        st.info("Add your API key to `.env`:")
        st.code("CONTEXTUAL_API_KEY=your_key_here")
        st.stop()
    
    st.divider()
    
    # Part 1 is creating a datastore
    st.subheader("Step 1: Datastore")
    if not st.session_state.datastore_id:
        datastore_name = st.text_input("Datastore Name", value="my-documents-datastore")
        if st.button("Create Datastore", type="primary", use_container_width=True):
            if datastore_name and client:
                try:
                    with st.spinner("Creating datastore..."):
                        datastores = client.datastores.list()
                        existing_datastore = next((ds for ds in datastores if ds.name == datastore_name), None)
                        
                        if existing_datastore:
                            st.session_state.datastore_id = existing_datastore.id
                            st.success("Using existing datastore")
                        else:
                            result = client.datastores.create(name=datastore_name)
                            st.session_state.datastore_id = result.id
                            st.success("Created new datastore")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.success("Datastore Ready")
        if st.button("Reset Datastore", use_container_width=True):
            st.session_state.datastore_id = ""
            st.session_state.agent_id = ""
            st.session_state.uploaded_docs = []
            st.rerun()
    
    # Part 2 is uploading documents to the datastore
    if st.session_state.datastore_id:
        st.subheader("Step 2: Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['pdf', 'txt', 'md', 'doc', 'docx', 'html']
        )
        
        if uploaded_files:
            st.write(f"Selected: {len(uploaded_files)} files")
            if st.button("Upload Documents", type="primary", use_container_width=True):
                try:
                    with st.spinner("Uploading..."):
                        for uploaded_file in uploaded_files:
                            client.datastores.documents.ingest(
                                st.session_state.datastore_id, 
                                file=uploaded_file
                            )
                            st.session_state.uploaded_docs.append(uploaded_file.name)
                        st.success(f"Uploaded {len(uploaded_files)} documents!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {e}")
        
        if st.session_state.uploaded_docs:
            with st.expander(f"{len(st.session_state.uploaded_docs)} Documents"):
                for doc_name in st.session_state.uploaded_docs:
                    st.write(f"{doc_name}")
    
    # Next part is creating the agent on that datastore
    if st.session_state.datastore_id:
        st.subheader("Step 3: Create Agent")
        if not st.session_state.agent_id:
            agent_name = st.text_input("Agent Name", value="my-rag-agent")
            if st.button("Create Agent", type="primary", use_container_width=True):
                if agent_name and client:
                    try:
                        with st.spinner("Creating agent..."):
                            agents = client.agents.list()
                            existing_agent = next((agent for agent in agents if agent.name == agent_name), None)
                            
                            if existing_agent:
                                st.session_state.agent_id = existing_agent.id
                                st.success("Using existing agent")
                            else:
                                result = client.agents.create(
                                    name=agent_name,
                                    description="RAG agent for document Q&A",
                                    datastore_ids=[st.session_state.datastore_id]
                                )
                                st.session_state.agent_id = result.id
                                st.success("Created new agent")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.success("Agent Ready")
            if st.button("Reset Agent", use_container_width=True):
                st.session_state.agent_id = ""
                st.rerun()
    
    st.divider()
    if st.session_state.chat_history:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    if st.button("Reset All", use_container_width=True):
        st.session_state.datastore_id = ""
        st.session_state.agent_id = ""
        st.session_state.chat_history = []
        st.session_state.uploaded_docs = []
        st.rerun()

st.title("Contextual AI RAG Chat")

if st.session_state.agent_id:
    st.success("RAG system ready! Ask questions about your documents below.")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Ask a question about your documents"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    response = client.agents.query.create(
                        agent_id=st.session_state.agent_id,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    if hasattr(response, 'message') and hasattr(response.message, 'content'):
                        answer = response.message.content
                    elif hasattr(response, 'content'):
                        answer = response.content
                    else:
                        answer = str(response)
                    
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    
            except Exception as e:
                error_msg = f"Error getting response: {e}"
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

else:
    if not st.session_state.datastore_id:
        st.info("**Step 1:** Create a datastore in the sidebar to get started")
        st.write("**What is a datastore?**")
        st.write("- A secure container for your documents")
        st.write("- Handles parsing, chunking, and indexing automatically")
        st.write("- Optimized for retrieval and search")
        
    elif not st.session_state.uploaded_docs:
        st.info("**Step 2:** Upload documents to your datastore")
        st.write("**Supported formats:**")
        st.write("- PDF documents")
        st.write("- Text files (.txt, .md)")
        st.write("- Word documents (.doc, .docx)")
        st.write("- HTML files")
        
    elif not st.session_state.agent_id:
        st.info("**Step 3:** Create an agent to start chatting")
        st.write("**What is an agent?**")
        st.write("- AI assistant connected to your documents")
        st.write("- Uses Contextual AI's advanced RAG system")
        st.write("- Provides grounded, accurate responses")
        
    # Show document preview if available
    if st.session_state.uploaded_docs:
        st.subheader("Uploaded Documents")
        cols = st.columns(min(3, len(st.session_state.uploaded_docs)))
        for i, doc_name in enumerate(st.session_state.uploaded_docs[:3]):
            with cols[i % 3]:
                st.info(f"{doc_name}")
        
        if len(st.session_state.uploaded_docs) > 3:
            st.write(f"... and {len(st.session_state.uploaded_docs) - 3} more documents")

st.caption("Powered by Contextual AI's Managed RAG Platform")