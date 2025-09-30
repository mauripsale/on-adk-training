from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from google.adk.tools import google_search
import asyncio
from dotenv import load_dotenv

load_dotenv()


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful assistant for user questions.",
    instruction="Answer user questions to the best of your knowledge. If you need use google_search tool.",
    tools=[google_search],
)

runner = InMemoryRunner(agent=root_agent)


async def main():

    
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )

    while True:

        user_input = input("User: ")
        if user_input == "exit":
            break

        content = UserContent(parts=[Part(text=user_input)])
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            for part in event.content.parts:
                print(part.text)


if __name__ == "__main__":
    asyncio.run(main())
