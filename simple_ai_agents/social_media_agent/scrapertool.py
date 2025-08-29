from langchain_scrapegraph.tools import SmartScraperTool
import os
from dotenv import load_dotenv

load_dotenv()

SGAI_API_KEY = os.getenv("SGAI_API_KEY")

# Initialize the tool (uses SGAI_API_KEY from environment)
tool = SmartScraperTool(api_key=SGAI_API_KEY)

# Extract information using natural language
result = tool.invoke(
    {
        "website_url": "https://x.com/3rdSon__",
        "user_prompt": "Extract the latest 10 tweets from this Twitter handle. Make sure they are the most recent 10 original tweets, not replies, retweets, or quoted tweets—only tweets authored directly by this account.",
    }
)

# Extract only the descriptions from the results
if "latest_tweets" in result:
    print("Latest Tweets (Descriptions only):")
    print("=" * 50)
    for i, tweet in enumerate(result["latest_tweets"], 1):
        print(f"{i}. {tweet['description']}")
        print("-" * 30)
else:
    print("No tweets found in the result")
    print("Full result:", result)
