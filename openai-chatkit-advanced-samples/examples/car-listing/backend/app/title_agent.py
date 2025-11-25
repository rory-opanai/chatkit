from agents import Agent
from chatkit.agents import AgentContext

title_agent = Agent[AgentContext](
    model="gpt-5-nano",
    name="Title generator",
    instructions="""
    Generate a short title for a conversation where a user is building a vehicle listing.
    The first user message in the conversation is included below.
    Do not just repeat the user message—summarize the intent.
    YOU MUST respond with 2-5 words without punctuation.
    """,
)
