from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='agent_speciale_pippo',
    description='Siamo in Italia, aiuta utenti in italiano',
    instruction='Answer user questions to the best of your knowledge',
)
