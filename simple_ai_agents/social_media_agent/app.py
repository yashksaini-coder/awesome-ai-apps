"""
Socisl Media Agent Streamlit App

A Streamlit application featuring two AI agents:
1. Style Analysis Agent: Scrapes user's tweets and analyzes tweeting style using Nebius
2. Tweet Generation Agent: Generates tweets using stored style and posts via Composio

This file contains the Streamlit interface while the agent logic is in twitter_agents.py
"""

import streamlit as st
import os
from twitter_agents import (
    initialize_memori,
    create_memory_tool_instance,
    scrape_user_tweets,
    analyze_tweeting_style,
    store_tweeting_style_in_memori,
    generate_tweet_with_style,
    post_tweet_via_composio,
    get_stored_tweeting_style,
    save_generated_tweet,
)
from create_tweet import create_tweet

# Page configuration
st.set_page_config(
    page_title="Social Media Agent",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "style_analysis" not in st.session_state:
    st.session_state.style_analysis = None
if "scraped_tweets" not in st.session_state:
    st.session_state.scraped_tweets = None
if "twitter_handle" not in st.session_state:
    st.session_state.twitter_handle = None
if "generated_tweet" not in st.session_state:
    st.session_state.generated_tweet = None
if "tweet_topic" not in st.session_state:
    st.session_state.tweet_topic = None


# Initialize Memori
@st.cache_resource
def get_memory_system():
    """Initialize Memori memory system"""
    try:
        memory_system = initialize_memori()
        return memory_system
    except Exception as e:
        st.error(f"Failed to initialize Memori: {e}")
        return None


# Initialize memory system
memory_system = get_memory_system()
if memory_system is None:
    st.stop()

# Create memory tool
memory_tool = create_memory_tool_instance(memory_system)

# Sidebar for Style Analysis Agent
with st.sidebar:
    st.image("./assets/nebius.png", width=150)

    # Load environment variables silently (not shown in frontend)
    composio_api_key = os.getenv("COMPOSIO_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    twitter_auth_config_id = os.getenv("TWITTER_AUTH_CONFIG_ID")
    user_id = os.getenv("USER_ID")

    # Only show Nebius and ScrapeGraph API Keys in frontend
    nebius_api_key = st.text_input(
        "Nebius API Key",
        value=os.getenv("NEBIUS_API_KEY", ""),
        type="password",
        help="Your Nebius API key",
    )

    st.image("./assets/scrapegraph.png", width=60)
    sgai_api_key = st.text_input(
        "ScrapeGraph API Key",
        value=os.getenv("SGAI_API_KEY", ""),
        type="password",
        help="Your ScrapeGraph (SGAI) API key",
    )

    if st.button("Save API Keys", use_container_width=True):
        saved_keys = []
        if nebius_api_key:
            os.environ["NEBIUS_API_KEY"] = nebius_api_key
            saved_keys.append("Nebius")
        if sgai_api_key:
            os.environ["SGAI_API_KEY"] = sgai_api_key
            saved_keys.append("ScrapeGraph")

        if saved_keys:
            st.success(f"✅ API keys saved successfully!")
        else:
            st.warning("Please enter at least one API key")

    st.markdown("---")
    st.subheader("🔍 Style Analysis")

    # Twitter handle input
    twitter_handle = st.text_input(
        "Enter Twitter Handle",
        placeholder="@username or username",
        help="Enter the Twitter handle you want to analyze (with or without @)",
    )

    if twitter_handle:
        st.session_state.twitter_handle = twitter_handle

        # Analyze button
        if st.button("🔍 Analyze Tweeting Style", type="primary"):
            with st.spinner("Scraping tweets..."):
                try:
                    # Scrape tweets
                    scraped_tweets = scrape_user_tweets(twitter_handle)
                    st.session_state.scraped_tweets = scraped_tweets

                    if scraped_tweets:
                        st.success(
                            f"✅ Successfully scraped {len(scraped_tweets)} tweets for analysis!"
                        )

                        # Show sample tweets
                        st.subheader("📝 Sample Tweets")
                        for i, tweet in enumerate(scraped_tweets[:3], 1):
                            st.markdown(
                                f"**Tweet {i}:** {tweet.get('description', 'N/A')}"
                            )

                        # Analyze style
                        with st.spinner("Analyzing tweeting style..."):
                            style_analysis = analyze_tweeting_style(scraped_tweets)

                            if style_analysis:
                                st.session_state.style_analysis = style_analysis

                                # Display analysis results
                                st.subheader("🎯 Style Analysis Results")

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown(
                                        f"**Tone:** {style_analysis.get('tone', 'N/A')}"
                                    )
                                    st.markdown(
                                        f"**Personality:** {style_analysis.get('personality', 'N/A')}"
                                    )
                                    st.markdown(
                                        f"**Language Style:** {style_analysis.get('language_style', 'N/A')}"
                                    )
                                    st.markdown(
                                        f"**Emoji Usage:** {style_analysis.get('emoji_usage', 'N/A')}"
                                    )

                                with col2:
                                    st.markdown(
                                        f"**Tweet Structure:** {style_analysis.get('tweet_structure', 'N/A')}"
                                    )
                                    st.markdown(
                                        f"**Common Topics:** {', '.join(style_analysis.get('common_topics', [])[:3])}"
                                    )
                                    st.markdown(
                                        f"**Writing Habits:** {', '.join(style_analysis.get('writing_habits', [])[:3])}"
                                    )

                                # Store in memory
                                with st.spinner("Storing style in memory..."):
                                    try:
                                        formatted_style = (
                                            store_tweeting_style_in_memori(
                                                memory_system,
                                                style_analysis,
                                                twitter_handle,
                                            )
                                        )
                                        if formatted_style:
                                            st.success(
                                                "✅ Style analysis complete & stored in memory!"
                                            )
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to store style")
                                    except Exception as e:
                                        st.error(f"❌ Error storing style: {e}")
                            else:
                                st.error("❌ Failed to analyze style")
                    else:
                        st.error("❌ No tweets found")

                except Exception as e:
                    st.error(f"❌ Error: {e}")

    st.markdown("---")
    st.subheader("📊 Current Status")

    # Show current style status
    has_session_style = (
        "style_analysis" in st.session_state and st.session_state.style_analysis
    )

    # Check if there's stored style in memory database
    has_stored_style = False
    try:
        stored_style = memory_tool.execute(query="twitter style tone personality")
        if stored_style and "No relevant memories found" not in str(stored_style):
            has_stored_style = True
    except:
        pass

    if has_session_style or has_stored_style:
        st.success("✅ Tweeting style profile found")
        if has_stored_style and not has_session_style:
            st.info("📄 Using previously stored Twitter style from memory")
        st.info("You can now generate tweets using the Tweet Generation Agent!")
    else:
        st.warning("⚠️ No tweeting style profile")
        st.info("Enter a Twitter handle and click 'Analyze Style' to get started")


def tweet_generation_agent():
    """Tweet Generation Agent interface"""
    # st.header("✍️ Tweet Generation")

    # Topic input for tweet generation
    topic = st.chat_input(
        "What would you like to tweet about? (e.g., The future of AI, My morning coffee, etc.)"
    )

    if topic:
        # Generate tweet
        with st.spinner("Generating tweet..."):
            try:
                tweet_content = generate_tweet_with_style(memory_tool, topic)

                if tweet_content:
                    # Store in session state
                    st.session_state.generated_tweet = tweet_content
                    st.session_state.tweet_topic = topic

                    st.subheader("🐦 Generated Tweet")

                    # Display the tweet
                    st.markdown(f"**{tweet_content}**")

                    # Character count
                    char_count = len(tweet_content)
                    if char_count > 280:
                        st.error(f"❌ Tweet too long: {char_count}/280 characters")
                    else:
                        st.success(f"✅ Tweet length: {char_count}/280 characters")

                    # Action buttons
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        # Copy to clipboard
                        if st.button("📋 Copy Tweet", use_container_width=True):
                            st.write("Tweet copied to clipboard!")

                    with col2:
                        # Post tweet button
                        if st.button(
                            "🚀 Post Tweet", type="primary", use_container_width=True
                        ):
                            with st.spinner("Posting tweet..."):
                                try:
                                    # Use the imported create_tweet function
                                    success = create_tweet(tweet_content)

                                    if success:
                                        st.success("🎉 Tweet posted successfully!")
                                        st.info(
                                            "Check your Twitter account to see the new tweet!"
                                        )

                                        # Save to memory
                                        try:
                                            save_generated_tweet(
                                                memory_system,
                                                topic,
                                                tweet_content,
                                            )
                                            st.success("💾 Tweet saved to memory!")
                                        except Exception as e:
                                            st.warning(
                                                f"Note: Could not save to memory: {e}"
                                            )
                                    else:
                                        st.error("❌ Failed to post tweet")
                                except Exception as e:
                                    st.error(f"❌ Error posting tweet: {e}")
                else:
                    st.error("❌ Failed to generate tweet")
            except Exception as e:
                st.error(f"❌ Error generating tweet: {e}")

    # Show stored tweet only when no new tweet is being generated
    elif st.session_state.generated_tweet and not topic:
        st.markdown("---")
        # st.subheader("🐦 Previously Generated Tweet")
        st.markdown(f"**{st.session_state.generated_tweet}**")

        # Character count
        char_count = len(st.session_state.generated_tweet)
        if char_count > 280:
            st.error(f"❌ Tweet too long: {char_count}/280 characters")
        else:
            st.success(f"✅ Tweet length: {char_count}/280 characters")

        # Action buttons for stored tweet
        col1, col2 = st.columns([1, 2])

        with col1:
            if st.button("📋 Copy Tweet", key="copy_stored", use_container_width=True):
                st.write("Tweet copied to clipboard!")

        with col2:
            if st.button(
                "🚀 Post Tweet",
                key="post_stored",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Posting tweet..."):
                    try:
                        success = create_tweet(st.session_state.generated_tweet)

                        if success:
                            st.success("🎉 Tweet posted successfully!")
                            st.info("Check your Twitter account to see the new tweet!")

                            # Save to memory
                            try:
                                save_generated_tweet(
                                    memory_system,
                                    st.session_state.tweet_topic,
                                    st.session_state.generated_tweet,
                                )
                                st.success("💾 Tweet saved to memory!")
                            except Exception as e:
                                st.warning(f"Note: Could not save to memory: {e}")
                        else:
                            st.error("❌ Failed to post tweet")
                    except Exception as e:
                        st.error(f"❌ Error posting tweet: {e}")

    elif not topic:
        st.markdown("### About this application")
        st.markdown("This application uses AI to generate engaging tweets for you!")
        st.markdown("**Simply type what you want to tweet about in the input above.**")
        st.markdown("**Features:**")
        st.markdown("• **Smart Generation**: Creates engaging tweets using AI")
        st.markdown("• **Direct Posting**: Posts tweets directly to Twitter")
        st.markdown(
            "• **Style Analysis**: Optional personalization available in the sidebar"
        )


def main():
    # Load and process SVG and PNG logos
    with open("./assets/gibson.svg", "r", encoding="utf-8") as gibson_file:
        gibson_svg = (
            gibson_file.read()
            .replace("\n", "")
            .replace("\r", "")
            .replace("  ", "")
            .replace('"', "'")
        )

    with open("./assets/composio.jpg", "rb") as composio_file:
        import base64

        composio_base64 = base64.b64encode(composio_file.read()).decode()
        composio_data_url = f"data:image/png;base64,{composio_base64}"

    # Create inline SVG elements for each logo
    gibson_svg_inline = f'<span style="height:80px; width:200px; display:inline-block; vertical-align:middle; margin-left:8px;margin-top:20px;margin-right:8px;">{gibson_svg}</span>'

    composio_svg_inline = f'<span style="height:80px; width:200px; display:inline-block; vertical-align:middle; margin-left:8px;margin-top:20px;margin-right:8px;"><img src="{composio_data_url}" style="height:80px; width:200px; object-fit:contain;"></span>'

    # Create title with embedded logos
    title_html = f"""
    <div style='display:flex; align-items:center; width:100%; padding:24px 0;'>
      <h1 style='margin:0; padding:0; font-size:2.5rem; font-weight:bold; display:flex; align-items:center;'>
        Social Media Agent with {gibson_svg_inline} Memori and {composio_svg_inline}
      </h1>
    </div>
    """

    # Display the styled title
    st.markdown(title_html, unsafe_allow_html=True)
    st.markdown("**AI-powered tweet generation that sounds exactly like you**")

    # Only show tweet generation on main page
    tweet_generation_agent()


if __name__ == "__main__":
    main()
