import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
from google.adk.tools import google_search

# Load environment variables from a .env file
load_dotenv()

async def main():
    print("Initializing agent...")
    root_agent = LlmAgent(
        model='gemini-2.5-flash', # Using a reliable model
        name='root_agent',
        description='A helpful assistant.',
        instruction='Answer user questions to the best of your knowledge. Be concise.',
        tools=[google_search]
    )

    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name="my_chat_app", session_service=session_service)

    session = await session_service.create_session(
        app_name=runner.app_name, user_id="test_user_chat"
    )
    print(f"Chat session started (ID: {session.id}). Type 'bye' to exit.")

    while True:
        user_input = input("\n> You: ")

        if user_input.lower().strip() == 'bye':
            print("<<< Agent: Goodbye!")
            break

        new_message = types.Content(role='user', parts=[types.Part(text=user_input)])
        final_response = "Sorry, I encountered an issue."

        print("...agent is thinking...")

        async for event in runner.run_async(
            user_id=session.user_id, session_id=session.id, new_message=new_message
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text

        print(f"<<< Agent: {final_response}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nChat interrupted. Exiting.")