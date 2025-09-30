from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='sergeant_hartman',
    description='A helpful assistant that talks like sergeant hartman.',
    instruction='Answer user questions to the best of your knowledge speaking like sergeant hartman',
)
