# In agent.py (Starter Code)
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.genai.types import UserContent, Part
import asyncio
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv

load_dotenv()
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# ============================================================================ 
# ARTIFACT-HANDLING TOOLS
# ============================================================================ 

async def extract_text(document_name: str, tool_context: ToolContext) -> str:
    """Extracts and cleans text from a document, saving it as an artifact."""
    extracted_content = f"EXTRACTED AND CLEANED TEXT FROM DOCUMENT: {document_name}"
    
    document = types.Part.from_text(text=extracted_content)
    version = await tool_context.save_artifact(f"{document_name}_extracted.txt", document)


    # TODO: 1. Create a types.Part from the `extracted_content`.
    # TODO: 2. Save the part as an artifact named f"{document_name}_extracted.txt".
    # TODO: 3. Return a confirmation message including the new version number.
    return f"Extraction complete. Saved artifact version {version}."

async def summarize_document(document_name: str, tool_context: ToolContext) -> str:
    """Generates a summary of a document from its extracted text artifact."""
    # TODO: 1. Load the latest version of the f"{document_name}_extracted.txt" artifact.
    # TODO: 2. If the artifact is not found, return a helpful error message.

    document = await tool_context.load_artifact(f"{document_name}_extracted.txt")
    
    summary_content = f"This is a concise summary of the document '{document_name}'."

    summary = types.Part.from_text(text=summary_content)
    
    version = await tool_context.save_artifact(f"{document_name}_summary.txt", summary)


    # TODO: 3. Create a types.Part from the `summary_content`.
    # TODO: 4. Save the summary as a new artifact named f"{document_name}_summary.txt".
    # TODO: 5. Return a confirmation message.
    return f"Summarization complete of {document_name}_extracted.txt. Saved artifact version {version} of {document_name}_summary.txt"

async def create_report(document_name: str, tool_context: ToolContext) -> str:
    """Creates a final report by compiling all artifacts for a document."""
    # TODO: 1. List all available artifacts using the tool_context.
    # TODO: 2. Filter the list to get only the names of artifacts for the current document.

    files = await tool_context.list_artifacts()

    filtered_files = [file for file in files if document_name in file]

    print(filtered_files)

    report = f"# Final Report for: {document_name}\n\n"
    # TODO: 3. Loop through your filtered list of artifact names. In the loop,
    # load each artifact and append its name and content to the `report` string.
    
    for file in filtered_files:
        file_artifact = await tool_context.load_artifact(file)
        print(file_artifact.text)
        report += f"""
{file_artifact.text}
"""

    # TODO: 4. Save the final `report` string as an artifact named
    # f"{document_name}_FINAL_REPORT.md".

    report_part = types.Part.from_text(text=report)

    print(report_part)


    await tool_context.save_artifact(f"{document_name}_FINAL_REPORT.md", report_part)

    # TODO: 5. Return a confirmation message.
    return "Report complete from all artifacts."

# ============================================================================ 
# AGENT DEFINITION
# ============================================================================ 

# TODO: Define the `root_agent`. Give it an instruction that tells it to run the
# pipeline in the correct order (extract -> summarize -> report) and register
# the three async tools.
root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='personal_tutor',
    description='A helpful assistant for user questions.',
    instruction='''
You will be provided with a document name.
Follow thi steps to provide me a report
Use the tool extract text to gather the informations
Summarize the document
Create a report with the information gathered
''',
    tools=[
        extract_text,
        summarize_document,
        create_report
    ]
)


artifact_service = InMemoryArtifactService()
session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name="my_artifact_app",
    session_service=session_service,
    artifact_service=artifact_service
)

async def main():

    
    session = await runner.session_service.create_session(
        app_name=runner.app_name, 
        user_id="test_user"
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
