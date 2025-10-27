from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
import asyncio
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# TOOLS: State Management & Memory Operations
# ============================================================================

def set_user_preferences(
    language: str,
    difficulty_level: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Set user learning preferences that should be stored persistently
    across all sessions for the current user.
    """
    tool_context.state['user:language'] = language
    tool_context.state['user:difficulty_level'] = difficulty_level
    # TODO: Store the language and difficulty_level in the tool_context.state.
    # Use the correct prefix for data that should persist for the user.
    print(f"TODO: Set user preferences: {language}, {difficulty_level}")
    return {'status': 'success', 'message': 'Preferences saved!'}


def start_learning_session(
    topic: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Start a new learning session. The current topic should only be
    remembered for the duration of the current conversation session.
    """
    # TODO: Store the topic in the tool_context.state.
    # Use the correct prefix for data that should only last for one session.
    print(f"TODO: Start session on topic: {topic}")
    return {'status': 'success', 'message': f'Started learning session: {topic}'}


def calculate_quiz_grade(
    correct_answers: int,
    total_questions: int,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Calculate a quiz grade. The raw percentage should be stored, but only
    for the current turn. It should be discarded immediately after this
    tool finishes.
    """
    percentage = (correct_answers / total_questions) * 100
    # TODO: Store the 'percentage' in the tool_context.state.
    # Use the correct prefix for data that is temporary for one turn.
    print(f"TODO: Calculate quiz grade. Percentage: {percentage}")
    return {'status': 'success', 'percentage': round(percentage, 1)}


# (Other tools like record_topic_completion, get_user_progress, etc. would also be completed here)

# ============================================================================
# AGENT DEFINITION
# ============================================================================

# TODO: Define the root_agent, including the tools you have just implemented.
# Make sure the agent's instruction can read an `app:course_version` from the state.


root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='personal_tutor',
    description='A helpful assistant for user questions.',
    instruction='''
You are the user tutor and must help the user practicing with some topics.
Use the tool set_user_preferences to save the user language and preferred difficulty level.
If the user wants to start a lesson use the start_learning_session tool to start the lesson
''',
    tools=[
        set_user_preferences,
        start_learning_session,
        calculate_quiz_grade
    ]
)


runner = InMemoryRunner(agent=root_agent)


async def main():

    
    session = await runner.session_service.create_session(
        app_name=runner.app_name, 
        user_id="test_user", 
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
