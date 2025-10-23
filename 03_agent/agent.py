import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai.types import UserContent, Part
import google.generativeai as genai

# Load environment variables from the .env file
load_dotenv()

# Configure the Google AI API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in the .env file")
genai.configure(api_key=api_key)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[google_search],
)

runner = InMemoryRunner(agent=root_agent)

async def main():
    # The session creation is asynchronous and must be done here
    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="test_user"
    )
    print("Chat started. Type 'bye', 'quit' or 'exit' to end.")

    while True:
        user_input = input("Prompt: ")
        if user_input.lower() in ["bye", "quit", "exit"]:
            print("Chat ended.")
            break

        content = UserContent(parts=[Part(text=user_input)])

        print("Gemini: ", end="", flush=True)
        # The runner execution is an asynchronous generator
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            for part in event.content.parts:
                print(part.text, end="", flush=True)
        print("\n") # Adds a new line after the complete response

if __name__ == '__main__':
    asyncio.run(main())
