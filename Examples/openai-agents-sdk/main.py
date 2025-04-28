from __future__ import annotations

import asyncio
import os
import resend
from openai import AsyncOpenAI
from agents import (
    Agent,
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
    RunConfig,
    Runner,
    function_tool,
    set_tracing_disabled,
)

# api_key = os.getenv("NEBIUS_API_KEY")
# if not api_key:
#     raise ValueError("NEBIUS_API_KEY is not set in the environment variables")

# Load environment variables
# Load environment variables
resend.api_key = os.getenv("RESEND_API_KEY")
api_key = os.getenv("NEBIUS_API_KEY")
if not resend.api_key:
    raise ValueError("RESEND_API_KEY is not set in the environment variables")
if not api_key:
    raise ValueError("NEBIUS_API_KEY is not set in the environment variables")
base_url = os.getenv("EXAMPLE_BASE_URL", "https://api.studio.nebius.ai/v1")
model_name = os.getenv("EXAMPLE_MODEL_NAME", "meta-llama/Meta-Llama-3.1-8B-Instruct")

client = AsyncOpenAI(base_url=base_url, api_key=api_key)
set_tracing_disabled(disabled=True)


class CustomModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=client)


CUSTOM_MODEL_PROVIDER = CustomModelProvider()


@function_tool
def send_email(to:str, subject:str, body:str):
    print(f"Sending email to {to}")
    params = {
        "from": "hi@arindammajumder.com",  # Replace with your verified sender email
        "to": [to],
        "subject": subject,
        "html": body,
    }
    try:
        response = resend.Emails.send(params)
        return {"status": "success", "message_id": response.get("id")}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def main():
    agent = Agent(name="Assistant", instructions="You only respond in haikus.", tools=[send_email])

    result = await Runner.run(
        agent,
        "Send an email to studioone.tech@gmail.com with the subject 'Test Email' and the body 'Demo for the Video'",
        run_config=RunConfig(model_provider=CUSTOM_MODEL_PROVIDER),
    )
    print(result.final_output)
 

if __name__ == "__main__":
    asyncio.run(main())