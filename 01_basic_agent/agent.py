from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='agente_scelto_pippo',
    description='A helpful assistant for user questions.',
    instruction='We are in Italy, help users in Italian',
)
