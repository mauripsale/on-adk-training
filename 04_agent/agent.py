import asyncio
import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

async def main():
    print("Initializing agent...")
    code_writer_agent = LlmAgent(
        model='gemini-2.5-flash',
    name='CodeWriterAgent',
    instruction="""You are a Python3.9+ Code Generator.
Based *only* on the user's request, write Python code that fulfills the requirement.
Remember to add type hints.
Generate robust code based on the principle of defensive programming.
Output *only* the complete Python code block, enclosed in triple backticks (```python ... ```). 
Do not add any other text before or after the code block.
""",
    description="Writes initial Python code based on a specification.",
    output_key="generated_code"
    )

    code_reviewer_agent = LlmAgent(
        model='gemini-2.5-flash',
    name='CodeReviewerAgent',
    instruction="""You are an expert Python Code Reviewer. 
    Your task is to provide constructive feedback on the provided code.

    **Code to Review:**
    ```python
    {generated_code}
    ```

**Review Criteria:**
1.  **Correctness:** Does the code work as intended? Are there logic errors? are the type hints correct?
2.  **Readability:** Is the code clear and easy to understand? Follows PEP 8 style guidelines?
3.  **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
4.  **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
5.  **Best Practices:** Does the code follow common Python best practices?

**Output:**
Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
If the code is excellent and requires no changes, simply state: "No major issues found."
Output *only* the review comments or the "No major issues" statement.
""",
    description="Reviews code and provides feedback.",
    output_key="review_comments",
)

    code_refactor_agent = LlmAgent(
        model='gemini-2.5-flash',
    name='CodeRefactorAgent',
    instruction="""You are a Python Code Refactoring AI.
Your goal is to improve the given Python code based on the provided review comments.

  **Original Code:**
  ```python
  {generated_code}
  ```

  **Review Comments:**
  {review_comments}

**Task:**
Carefully apply the suggestions from the review comments to refactor the original code.
If the review comments state "No major issues found," return the original code unchanged.
Ensure the final code is complete, functional, and includes necessary imports and docstrings.

**Output:**
Output *only* the final, refactored Python code block, enclosed in triple backticks (```python ... ```). 
Do not add any other text before or after the code block.
""",
    description="Refactors code based on review comments.",
    output_key="refactored_code",
)
    code_pipeline_agent = SequentialAgent(
        name="CodePipelineAgent",
        sub_agents=[code_writer_agent, code_reviewer_agent, code_refactor_agent]
    )

    root_agent = code_pipeline_agent
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