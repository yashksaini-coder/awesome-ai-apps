#!/usr/bin/env python3
"""
Test file for the post_tweet_via_composio function
"""

import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from twitter_agents import post_tweet_via_composio


def test_post_tweet():
    """Test the post_tweet_via_composio function"""

    # Test tweet text
    test_tweet = "🧪 Testing the Twitter Post Agent! This is a test tweet to verify the posting functionality works correctly. #Testing #TwitterBot #AI"

    print("🧪 Testing post_tweet_via_composio function")
    print("=" * 60)
    print(f"Test tweet: {test_tweet}")
    print(f"Tweet length: {len(test_tweet)} characters")
    print("=" * 60)

    try:
        # Test the function
        result = post_tweet_via_composio(test_tweet)

        if result:
            print("✅ SUCCESS: Tweet posted successfully!")
            print("Check your Twitter account to see the test tweet.")
        else:
            print("❌ FAILED: Tweet posting failed.")

    except Exception as e:
        print(f"❌ ERROR: Exception occurred: {e}")
        print(f"Error type: {type(e).__name__}")


if __name__ == "__main__":
    test_post_tweet()
