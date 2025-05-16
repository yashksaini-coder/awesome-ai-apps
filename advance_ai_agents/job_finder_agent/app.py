import streamlit as st
import asyncio
import os
import logging
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
)
from agents.mcp import MCPServer, MCPServerStdio
from openai import AsyncOpenAI
from dotenv import load_dotenv
import threading
import nest_asyncio
nest_asyncio.apply()
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('job_finder.log')
    ]
)
logger = logging.getLogger(__name__)

# Global variables for MCP initialization
_mcp_server = None
_init_lock = threading.Lock()
_initialized = False
_initialization_in_progress = False
load_dotenv()

# Set page config
st.set_page_config(
    page_title="LinkedIn Profile Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state for storing analysis results
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = ""
if 'is_analyzing' not in st.session_state:
    st.session_state.is_analyzing = False

async def run_analysis(mcp_server: MCPServer, linkedin_url: str):
    logger.info(f"Starting analysis for LinkedIn URL: {linkedin_url}")
    api_key = os.environ["NEBIUS_API_KEY"]
    base_url = "https://api.studio.nebius.ai/v1" 
    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    set_tracing_disabled(disabled=True)

    linkedin_agent = Agent(
        name="LinkedIn Profile Analyzer",
        instructions=f"""You are a LinkedIn profile analyzer.
        Analyze profiles for:
        
        - Professional experience and career progression
        - Education and certifications
        - Core skills and expertise
        - Current role and company
        - Previous roles and achievements
        - Industry reputation (recommendations/endorsements)
        
        Provide a structured analysis with bullet points and a brief executive summary.
        
        NOTE: If the user has no experience, just say "No experience found" and don't make up any information. Also if any of the information is not available, just say "Not available" and don't make up any information.
        DISCLAIMER: This Agent should call the tool to get the information. Once the tool is called, it will return the information in the response. It should not call the tool Multiple times after the tool is called.
        """,
        mcp_servers=[mcp_server],
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )

    job_suggestions_agent = Agent(
        name="Job Suggestions",
        instructions=f"""You are a domain classifier that identifies the primary professional domain from a LinkedIn profile.

        Select ONE domain from:
        - Software Engineering (for programming, development, technical skills)
        - Design & UI/UX (for design, user experience, visual skills)
        - Product Management (for product strategy, roadmap, feature planning)
        - Recruiting & HR (for talent acquisition, HR operations, people management)
        - Sales (for sales, business development)
        - Science (for research, data science, scientific expertise)
        - Marketing (for Content Writing, Technical Writing, Developer Relations,Developer Advocacy, advertising, brand management)
        Rules:
        - Choose based on PRIMARY skills and experience
        - If multiple domains exist, pick the most recent/relevant one
        - Default to Software Engineering if unclear
        - Return "No experience found" for empty profiles
        - Never make up or assume skills

        Format response as JSON:
        {{
            "selected_domain": "chosen domain",
            "confidence_score": 0-100,
            "selection_reason": "brief explanation"
        }}
        """,
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )

    url_generator_agent = Agent(
        name="URL Generator",
        instructions=f"""You are a URL generator that creates Y Combinator job board URLs based on domains.

        Input: JSON from job suggestions agent with format:
        {{
            "selected_domain": "domain name",
            "confidence_score": number,
            "selection_reason": "reason"
        }}

        Map domains to URLs:
        - "Software Engineering" -> "ycombinator.com/jobs/role/software-engineer"
        - "Design & UI/UX" -> "ycombinator.com/jobs/role/designer"
        - "Product Management" -> "ycombinator.com/jobs/role/product-manager"
        - "Recruiting & HR" -> "ycombinator.com/jobs/role/recruiting-hr"
        - "Sales" -> "ycombinator.com/jobs/role/sales-manager"
        - "Science" -> "ycombinator.com/jobs/role/science"
        - "Marketing" -> "ycombinator.com/jobs/role/marketing"

        Output format:
        {{
            "job_board_url": "mapped url",
            "domain": "original domain"
        }}

        Rules:
        - Return exact URL match for domain
        - If domain not found, return "ycombinator.com/jobs"
        - Keep original domain in output
        """,
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )

    url_parser_agent = Agent(
        name="URL Parser",
        instructions=f"""You are a URL parser that transforms Y Combinator authentication URLs into direct job URLs.

        Input: Job listings with authentication URLs in format:
        ## Job Matches for [Domain]
        ### [Job Title]
        - **Company:** [Company Name]
        - **Type:** [Job Type]
        - **Location:** [Location]
        - **Apply:** [Auth URL]

        Rules:
        1. Extract job_id from the authentication URL
           - Look for 'signup_job_id=' parameter
           - Example: from '...signup_job_id=75187...' extract '75187'
        
        2. Create new direct URL format:
           - Base URL: 'https://www.workatastartup.com/jobs/'
           - Append job_id
           - Example: 'https://www.workatastartup.com/jobs/75187'

        3. Replace the Apply URL in each job listing with the new direct URL

        Output format:
        ## Job Matches for [Domain]
        ### [Job Title]
        - **Company:** [Company Name]
        - **Type:** [Job Type]
        - **Location:** [Location]
        - **Apply:** [Direct URL]

        Note: Keep all other information exactly the same, only transform the Apply URLs.
        """,
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )

    Job_search_agent = Agent(
        name="Job Finder",
        instructions=f"""You are a job finder that extracts job listings from Y Combinator's job board.

        Steps:
        1. Take the URL from job_link_result agent's JSON response
        2. Use the provided URL to fetch job listings

        3. For each job listing, extract ONLY these fields:
           - Company name (from the company link text)
           - Job title (from the job link text)
           - Job type (Full-time/Part-time/Contract)
           - Location (including remote status)
           - Apply URL (from the Apply button href)

        4. Format output as:
        ## Job Matches for [Domain]
        ### [Job Title]
        - **Company:** [Company Name]
        - **Type:** [Job Type]
        - **Location:** [Location]
        - **Apply:** [Apply URL]

        Rules:
        - Only extract information from actual job listings
        - Skip navigation links, footer content, and other non-job elements
        - Use exact text from the job listing
        - Return "No jobs found" if no listings are available
        - Ignore job categories and location filters
        - Do not include any additional information not present in the job listing

        Note: No information should be added to the response that is not provided in the input. Don't make up any information.
        IMPORTANT: Once the tool is called, it will return the information in the response. It should not call the tool Multiple times after the tool is called. Call the tool only once.
        """,
        mcp_servers=[mcp_server],
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )
    
    summary_agent = Agent(
        name="Summary Agent",
        instructions=f"""You are a summary agent that creates comprehensive career analysis reports.
        Your task is to:
        1. Take the inputs from various agents (LinkedIn analysis, job suggestions, and job matches)
        2. Create a well-structured, professional summary in markdown format that includes:
           - A concise profile summary
           - Top skills identified
           - Recommended career paths
           - Detailed role suggestions with reasons and requirements
           - Current job matches with match scores
           - Skills to develop
           - Career development suggestions
        
        Format your response in markdown with the following structure:
        ```markdown
        ## 👤 Profile Summary
        [Write a brief summary of the person's career profile]

        ## 🎯 Your Top Skills:
        - [Skill 1]
        - [Skill 2]

        ...

        ## 💡 Suggested Roles:
        ### [Role Title]
        - **Why this role?** [Explanation]
        - **Required Skills:** [Skill 1, Skill 2, ...]
        - **Potential Companies:** [Company 1, Company 2, ...]
        - **Growth Potential:** [Growth opportunities]
        - **Salary Range:** [Salary range if available]

        ## 💼 Current Job Matches:
        ### [Job Title] at [Company]
          - [Brief description]
          - Match Score: [Score]%
          - [Apply Here]([Job URL])
        ...
        ```
        
        Note: No information should be added to the response that is not provided in the input. Don't make up any information.
        Ensure your response is well-formatted markdown that can be directly displayed.""",
        model=OpenAIChatCompletionsModel(
            model="meta-llama/Llama-3.3-70B-Instruct",
            openai_client=client
        )
    )
    
    query = f"""Analyze the LinkedIn profile at {linkedin_url}.
    Focus on gathering comprehensive information about the person's professional background.
    Then, find the best job for the user based on their profile.
    """

    try:
        # Get LinkedIn profile analysis
        logger.info("Running LinkedIn profile analysis")
        linkedin_result = await Runner.run(starting_agent=linkedin_agent, input=query)
        logger.info("LinkedIn profile analysis completed")

        # Get job suggestions
        logger.info("Getting job suggestions")
        suggestions_result = await Runner.run(starting_agent=job_suggestions_agent, input=linkedin_result.final_output)
        logger.info("Job suggestions completed")

        # Get specific job matches
        logger.info("Getting job matches")
        job_link_result = await Runner.run(starting_agent=url_generator_agent, input=suggestions_result.final_output)
        logger.info("Job link generation completed")

        job_search_result = await Runner.run(starting_agent=Job_search_agent, input=job_link_result.final_output)
        logger.info("Job search completed")

        # Parse URLs to get direct job links
        logger.info("Parsing job URLs")
        parsed_urls_result = await Runner.run(starting_agent=url_parser_agent, input=job_search_result.final_output)
        logger.info("URL parsing completed")

        # Create a single input for the summary agent
        logger.info("Generating final summary")
        summary_input = f"""LinkedIn Profile Analysis:
        {linkedin_result.final_output}

        Job Suggestions:
        {suggestions_result.final_output}

        Job Matches:
        {parsed_urls_result.final_output}

        Please analyze the above information and create a comprehensive career analysis report in markdown format."""
        
        # Get final summary with a single call
        summary_result = await Runner.run(starting_agent=summary_agent, input=summary_input)
        logger.info("Summary generation completed")
        st.session_state.analysis_result = summary_result.final_output

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        st.error(f"Error during analysis: {str(e)}")
    finally:
        st.session_state.is_analyzing = False
        logger.info("Analysis process completed")

async def initialize_mcp_server():
    """Initialize MCP server using the existing event loop."""
    global _mcp_server, _initialized, _initialization_in_progress
    
    if _initialized:
        logger.info("MCP server already initialized")
        return _mcp_server
    
    with _init_lock:
        if _initialized:
            return _mcp_server
            
        if _initialization_in_progress:
            logger.info("Waiting for MCP server initialization to complete")
            while _initialization_in_progress:
                await asyncio.sleep(0.1)
            return _mcp_server
        
        _initialization_in_progress = True
    
    try:
        logger.info("Connecting to Bright Data MCP...")
        server = MCPServerStdio(
            cache_tools_list=False,
            params={
                "command": "npx",
                "args": ["-y", "@brightdata/mcp"],
                "env": {
                    "API_TOKEN": os.environ["BRIGHT_DATA_API_KEY"],
                    "WEB_UNLOCKER_ZONE": "mcp_unlocker",
                    "BROWSER_AUTH": os.environ["BROWSER_AUTH"],
                }
            }
        )
        
        await asyncio.wait_for(server.__aenter__(), timeout=10)
        logger.info("MCP server initialized successfully")
        
        _mcp_server = server
        _initialized = True
        
        # Register cleanup on exit
        import atexit
        def cleanup_mcp():
            global _mcp_server
            if _mcp_server:
                logger.info("Closing MCP server connection...")
                try:
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(_mcp_server.__aexit__(None, None, None))
                    loop.close()
                    logger.info("MCP server connection closed successfully.")
                except Exception as e:
                    logger.error(f"Error closing MCP connection: {e}", exc_info=True)
                finally:
                    _mcp_server = None
        
        atexit.register(cleanup_mcp)
        
        return server
        
    except Exception as e:
        logger.error(f"Error initializing MCP server: {e}", exc_info=True)
        return None
    finally:
        _initialization_in_progress = False

async def wait_for_initialization():
    """Wait for MCP initialization to complete."""
    global _initialized
    
    if not _initialized:
        logger.info("Starting MCP initialization...")
        await initialize_mcp_server()
    
    return _initialized

async def analyze_profile(linkedin_url: str):
    try:
        # Wait for MCP server initialization
        if not await wait_for_initialization():
            logger.error("Failed to initialize MCP server")
            st.error("Failed to initialize MCP server")
            return
            
        await run_analysis(_mcp_server, linkedin_url)
    except Exception as e:
        logger.error(f"Error analyzing LinkedIn profile: {str(e)}", exc_info=True)
        st.error(f"Error analyzing LinkedIn profile: {str(e)}")
        st.session_state.is_analyzing = False

def main():
    with open("./assets/linkedin.png", "rb") as linkedin_file:
        linkedin_base64 = base64.b64encode(linkedin_file.read()).decode()
    with open("./assets/bright-data-logo.png", "rb") as bright_data_file:
        bright_data_base64 = base64.b64encode(bright_data_file.read()).decode()       
        # Create title with embedded images
        title_html = f"""
        <div style="display: flex; align-items: center; gap: 0px; margin: 0; padding: 0;">
            <h1 style="margin: 0; padding: 0;">
            Job Searcher Agent with 
            <img src="data:image/png;base64,{bright_data_base64}" style="height: 110px; margin: 0; padding: 0;"/>
            </h1>
        </div>
        """
    st.markdown(title_html, unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)

    with st.sidebar:
        st.image("./assets/Nebius.png", width=150)
        
        # API key input
        api_key = st.text_input("Enter your API key", type="password")
        
        st.divider()
        
        # LinkedIn URL input
        st.subheader("Enter LinkedIn Profile URL")
        linkedin_url = st.text_input("LinkedIn URL", placeholder="https://www.linkedin.com/in/username/")
        
        # Analyze button
        if st.button("Analyze Profile", type="primary", disabled=st.session_state.is_analyzing):
            if not linkedin_url:
                st.error("Please enter a LinkedIn profile URL")
                return
            if not api_key:
                st.error("Please enter your API key")
                return

            st.session_state.is_analyzing = True
            st.session_state.analysis_result = ""
            
            # Create and run the event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(analyze_profile(linkedin_url))
            finally:
                loop.close()

    # Results section
    if st.session_state.analysis_result:
        st.markdown("---", unsafe_allow_html=True)
        st.subheader("Analysis Results")
        st.markdown(st.session_state.analysis_result)

    # Show loading state
    if st.session_state.is_analyzing:
        st.markdown("---", unsafe_allow_html=True)
        with st.spinner("Analyzing profile... This may take a few minutes."):
            st.empty()

if __name__ == "__main__":
    main()