import os
import asyncio
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from google.adk.tools import google_search

code_writer_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='Claude_Writer',
    instruction="""You are a Python Code Generator.
    Based *only* on the user's request, write Python code that fulfills the requirement.
    Output *only* the complete Python code block, enclosed in triple backticks (```python ... ```). 
    Do not add any other text before or after the code block.
    """,
    description="Writes initial Python code based on a specification.",
    output_key="generated_code"   
)

code_reviewer_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='Jack_The_Reviewer',
    instruction="""You are a Python Code Reviewer.
    Review {generated_code}
    """,
    description="Review Python code ",
    output_key="reviewed_code"   
)

code_refactor_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='RefacThor',
    instruction="""You are a Python Code Refactor.
    Refact {reviewed_code}
    """,
    description="Refact Python code "
)

coordinator = LlmAgent(
    model='gemini-2.5-flash',
    name='Coolrdinator',
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactor_agent]
)


USER_ID = "test_user"
MODEL = "gemini-2.5-flash" # Use a valid model

load_dotenv()

runner = InMemoryRunner(agent=coordinator)

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
                    if part.text is not None:
                        response_text += part.text
        
        print(f"Agent: {response_text}")

if __name__ == "__main__":
    asyncio.run(main())
