from agno.agent import Agent
from typing import Iterator
from agno.team import Team, TeamRunOutputEvent
from agno.models.groq import Groq
from agno.tools.gmail import GmailTools
from agno.tools.googlesheets import GoogleSheetsTools
from agno.tools.googlecalendar import GoogleCalendarTools
import dotenv
from dotenv import load_dotenv
from agno.utils.pprint import pprint_run_response
from agno.db.sqlite import SqliteDb
import os


load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
groq_base_url = os.getenv("GROQ_BASE_URL")
db = SqliteDb(db_file="tmp/data.db")


email_agent = Agent(
    model=Groq(id="qwen/qwen3-32b", api_key=groq_api_key),
    markdown=True,
    tools=[GmailTools(credentials_path="credentials.json", port=8090)],
    description="You are a Gmail reading specialist that can search and read emails.",
    instructions=[
        "Use the tools to search and read emails from Gmail.",
        "Focus on extracting key details such as sender, subject, and body of the email.",
        "Summarize the body of the email concisely.",
        "Never fabricate email content; only use the information available in the emails.",
        "If no emails are found, respond with 'No emails found.'",
    ],
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    read_chat_history=True,
)


calendar_agent = Agent(
    model=Groq(id="qwen/qwen3-32b", api_key=groq_api_key),
    tools=[
        GoogleCalendarTools(
            credentials_path="credentials.json",
            allow_update=True,
        )
    ],
    instructions=[
        """
    You are a scheduling assistant.
    You should help users to perform these actions in their Google calendar:
        - get their scheduled events from a certain date and time
        - create events based on provided details
        - update existing events
        - delete events
        - find available time slots for scheduling
        - all times are in Indian Standard Time (IST)
    """
    ],
    add_datetime_to_context=True,
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    read_chat_history=True,
)


team = Team(
    name="Productivity Agent",
    members=[email_agent, calendar_agent],
    description="Team to extract emails, filter important emails  and update Google Calendar based on email content.",
    model=Groq(id="qwen/qwen3-32b", api_key=groq_api_key),
    instructions=[
        f"First, use the email agent to find and read the latest emails and extract the important emails with the important details such as sender, subject, and summarized body.",
        "Then, use the calendar agent to update Google Calendar based on the email content.",
        "If an Event is to be added, updated or deleted, ensure to provide all necessary details such as event name, date, time, and any other relevant information.",
        "If some details are missing for updating or adding an event, make reasonable assumptions based on the email content.",
        "Collaborate effectively to ensure accurate data extraction and updating.",
        "Output the final task updates made to the Google Sheet.",
    ],
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    read_team_history=True,
)


prompt = "Hello"
print("🧠 Smart Scheduler Assistant is running. Type 'exit' to quit.\n")
user_input = prompt
while True:

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye 👋")
        break

    response = team.print_response(user_input)
    print("\nAgent:", response, "\n")
    user_input = input("You: ")
