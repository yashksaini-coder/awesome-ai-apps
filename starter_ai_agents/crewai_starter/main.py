from crewai import Agent, Task,LLM
import os
from dotenv import load_dotenv
from crewai import Crew, Process

load_dotenv()

default_llm=LLM(
        model="openai/meta-llama/Meta-Llama-3.1-70B-Instruct",
        base_url="https://api.studio.nebius.com/v1/",
        api_key=os.getenv("NEBIUS_API_KEY")
),

# Create a researcher agent
researcher = Agent(
  role='Senior Researcher',
  goal='Discover groundbreaking technologies',
  verbose=True,
  llm=LLM(
        model="openai/meta-llama/Meta-Llama-3.1-70B-Instruct",
        base_url="https://api.studio.nebius.com/v1/",
        api_key=os.getenv("NEBIUS_API_KEY")
),

  backstory='A curious mind fascinated by cutting-edge innovation and the potential to change the world, you know everything about tech.'
)

# Task for the researcher
research_task = Task(
  description='Identify the next big trend in AI',
  expected_output='5 paragraphs on the next big AI trend',
  agent=researcher  # Assigning the task to the researcher
)

# Instantiate your crew
tech_crew = Crew(
  agents=[researcher],
  tasks=[research_task],
  process=Process.sequential  # Tasks will be executed one after the other
)

# Begin the task execution
tech_crew.kickoff()