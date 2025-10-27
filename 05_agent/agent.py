import time
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from google.adk.events import Event, EventActions
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
        app_name=runner.app_name, 
        user_id="test_user", 
        state={"foo": "bar", "bar": "foo", "baz": "qux", "counter": 0}
    )

    print(f"Initial session state: {session.state}")


    while True:

        state_changes = {
            "counter": session.state["counter"] + 1,
            "foo": "bar"*session.state["counter"],
            "bar": "foo"*session.state["counter"],
            "baz": "qux"*session.state["counter"]
        }

        actions_with_update = EventActions(state_delta=state_changes)

        user_input = input("User: ")
        if user_input == "exit":
            break

        current_time = time.time()

        system_event = Event(
            invocation_id="inv_login_update",
            author="system", # Or 'agent', 'tool' etc.
            actions=actions_with_update,
            timestamp=current_time
        )

        content = UserContent(parts=[Part(text=user_input)])
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            for part in event.content.parts:
                print(part.text)

        await runner.session_service.append_event(session, system_event)

        updated_session = await runner.session_service.get_session(app_name=runner.app_name,
                                            user_id=session.user_id,
                                            session_id=session.id)
        print(f"State after event: {updated_session.state}")


if __name__ == "__main__":
    asyncio.run(main())
