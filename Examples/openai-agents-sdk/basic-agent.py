from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("NEBIUS_API_KEY")
if not api_key:
    raise ValueError("NEBIUS_API_KEY is not set in the environment variables")

model = OpenAIChatCompletionsModel(
    model= "openai/meta-llama/Meta-Llama-3.1-8B-Instruct",
    openai_client=AsyncOpenAI(base_url="https://api.studio.nebius.ai/v1", api_key=api_key)
)

agent = Agent(
    name="Assistant",
    instruction="You're a Expert Doctor",
    model=model
)

result = Runner.run(agent,"Give me a diet plan as a 18 y/o boy")

print(result)
