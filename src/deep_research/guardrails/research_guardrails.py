from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from pydantic import BaseModel


class ResearchOutput(BaseModel):
    reasoning: str
    is_research_request: bool


research_guardrail_agent = Agent(
    name="Input guardrail check on research",
    instructions="Check if the user is asking you to do research.",
    output_type=ResearchOutput,
)


@input_guardrail
async def research_input_guardrail(
    context: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    """This is an input guardrail function, which happens to call an agent to check if the input
    is a research.
    """
    result = await Runner.run(research_guardrail_agent, input, context=context.context)
    final_output = result.final_output_as(ResearchOutput)

    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_research_request,
    )
