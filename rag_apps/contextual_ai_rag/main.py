import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Contextual AI RAG Chat",
    layout="wide"
)

st.title("Contextual AI RAG Chat")
st.write("Upload documents and chat with your data using Contextual AI's managed RAG platform.")

# Check for API key in environment
contextual_api_key = os.getenv("CONTEXTUAL_API_KEY")

# Sidebar for setup info
with st.sidebar:
    st.header("Setup")
    if contextual_api_key:
        st.success("Contextual AI API key loaded")
    else:
        st.error("Missing CONTEXTUAL_API_KEY")
        st.info("Please add your API key to a `.env` file:")
        st.code("CONTEXTUAL_API_KEY=your_api_key_here")
