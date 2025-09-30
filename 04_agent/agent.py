from . import prompt
from google.adk.agents import ParallelAgent, LlmAgent, SequentialAgent
from .tools.rag_tool import get_context_chunks
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
import asyncio
from dotenv import load_dotenv

GEMINI_MODEL = "gemini-2.5-flash"

rag_agent_same_language = LlmAgent(
    name="SameLanguageRagAgent",
    model=GEMINI_MODEL,
    instruction=prompt.RAG_SAME_LANGUAGE,
    description="An agent that performs a similarity search using the user query",
    tools=[get_context_chunks],
    output_key="same_language_context"
)

rag_agent_other_language = LlmAgent(
    name="OtherLanguageRagAgent",
    model=GEMINI_MODEL,
    instruction=prompt.RAG_OTHER_LANGUAGE,
    description="An agent that performs a similarity search using the translated user query",
    tools=[get_context_chunks],
    output_key="other_language_context"
)

parallel_research_agent = ParallelAgent(
    name="ParallelResearchAgent",
    sub_agents=[rag_agent_same_language, rag_agent_other_language],
    description="Runs multiple agents to gather informations"
)

answer_agent = LlmAgent(
    name="AnswerAgent",
    model=GEMINI_MODEL,
    description="Agent to answer questions using the context with links and images as it's knowledge.",
    instruction=prompt.RAG_AGENT_INSTR,
)

sequential_pipeline_agent = SequentialAgent(
     name="ResearchAndSynthesisAgent",
     sub_agents=[parallel_research_agent, answer_agent],
     description="Coordinates parallel research and answer to the user."
)

question_detector_agent = LlmAgent(
    name="QuestionDetectorAgent",
    model=GEMINI_MODEL,
    sub_agents=[sequential_pipeline_agent],
    description="Question detector agent that greets the user and perform basic conversation if it detects the user is asking a question reguarding some issue it pass the query to the next agent",
    instruction=prompt.QUESTION_INSTR
)

root_agent = question_detector_agent

load_dotenv()

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
