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
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Why Contextual AI Datastores?**")
            st.write("- **Enterprise-grade parsing** - Handles complex PDFs, tables, charts automatically")
            st.write("- **No vector database setup** - Managed infrastructure scales for you") 
            st.write("- **Advanced document processing** - Preserves document structure and hierarchy")
            st.write("- **Built-in security** - Data isolation and compliance-ready")
        
        with col2:
            st.write("**vs Traditional RAG Approaches:**")
            st.write("- No need to configure embedding models")
            st.write("- No chunking strategy decisions") 
            st.write("- No vector database management")
            st.write("- No infrastructure scaling concerns")
            
    elif not st.session_state.uploaded_docs:
        st.info("**Step 2:** Upload documents to your datastore")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Advanced Document Processing:**")
            st.write("- **PDFs** - Complex tables, charts, multi-column layouts")
            st.write("- **Office docs** - Word, PowerPoint with embedded content") 
            st.write("- **Web content** - HTML with proper structure preservation")
            st.write("- **Text files** - Markdown, plain text with formatting")
        
        with col2:
            st.write("**What Happens Next:**")
            st.write("- Documents are parsed with hierarchy awareness")
            st.write("- Content is automatically chunked optimally")
            st.write("- Embeddings generated with state-of-the-art models")
            st.write("- Ready for intelligent retrieval in minutes")
            
    elif not st.session_state.agent_id:
        st.info("**Step 3:** Create an agent to start chatting")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Contextual AI Agent Capabilities:**")
            st.write("- **Grounded responses** - Always cite source documents")
            st.write("- **Multi-document synthesis** - Compare and analyze across files")
            st.write("- **Advanced retrieval** - Beyond simple similarity search") 
            st.write("- **Hallucination prevention** - Built-in accuracy safeguards")
        
        with col2:
            st.write("**Built-in Quality Features:**")
            st.write("- **Source attribution** - See exactly which pages were referenced")
            st.write("- **LMUnit evaluation** - Automated quality scoring")
            st.write("- **Retrieval visualization** - View document excerpts used")
            st.write("- **Performance analytics** - Track accuracy and relevance")
            
    if st.session_state.uploaded_docs:
        st.subheader("Document Collection Ready")
        st.write(f"**{len(st.session_state.uploaded_docs)} documents** processed and indexed:")
        
        cols = st.columns(min(4, len(st.session_state.uploaded_docs)))
        for i, doc_name in enumerate(st.session_state.uploaded_docs[:4]):
            with cols[i % 4]:
                with st.container():
                    st.write(f"**{doc_name}**")
                    st.caption("Processed & Indexed")
        
        if len(st.session_state.uploaded_docs) > 4:
            st.write(f"**Plus {len(st.session_state.uploaded_docs) - 4} more documents** in your knowledge base")
            
        st.write("**Next:** Create an agent in the sidebar to start querying these documents")

st.caption("Powered by Contextual AI's Managed RAG Platform")