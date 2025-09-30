import asyncio
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from google.adk.tools import google_search

# --- Constants ---

USER_ID = "test_user"
MODEL = "gemini-2.5-flash" # Use a valid model

load_dotenv()

root_agent = LlmAgent(
    model=MODEL,
    name="Pino_Germani",
    instruction="You are a friendly and helpful assistant. Your goal is to have a natural conversation with the user. Ask questions to keep the conversation going. Remember the user's name and other details they share with you.",
    tools=[google_search]
)

runner = InMemoryRunner(agent=root_agent)

async def main():   
    
    sessionid = "sessionid"
    await runner.session_service.create_session(app_name=runner.app_name, user_id=USER_ID, session_id = sessionid)
    
    print("Starting chat. Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        content = Content(parts=[Part(text=user_input)], role="user")

        response_text = ""
        async for event in runner.run_async(user_id=USER_ID, session_id=sessionid, new_message=content):
                for part in event.content.parts:
                    response_text += part.text
        
        print(f"Agent: {response_text}")

if __name__ == "__main__":
    asyncio.run(main())