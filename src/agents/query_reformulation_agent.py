from pydantic import BaseModel

from agents import Agent
from src.agents.guardrails import input_validation_guardrail, research_input_guardrail

INSTRUCTIONS = (
    "You are a helpful research assistant. Analyze the provided search query,"
    "identify its key concepts, implicit intentions, and potential knowledge gaps, "
    "then generate an expanded version of the query."
)


class QueryOutput(BaseModel):
    query: str


query_reformulation_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    input_guardrails=[input_validation_guardrail, research_input_guardrail],
    output_type=QueryOutput,
)
