import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from google.adk.tools import google_search

TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_folder")

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='FilePippo',
    instruction='Help the user manage their files. You can list files, read files, etc.',
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx.cmd',
                    args=[
                        "-y", # Argument for npx to auto-confirm install
                        "@modelcontextprotocol/server-filesystem",
                        # IMPORTANT: This MUST be an ABSOLUTE path to a folder the
                        # npx process can access.
                        # Replace with a valid absolute path on your system.
                        # For example: "/Users/youruser/accessible_mcp_files"
                        # or use a dynamically constructed absolute path:
                        os.path.abspath(TARGET_FOLDER_PATH),
                    ],
                ),
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
        )
    ],
)



# --- Constants ---

USER_ID = "test_user"
MODEL = "gemini-2.5-flash" # Use a valid model

load_dotenv()


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
