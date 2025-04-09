from agents import Agent, function_tool
from agents.model_settings import ModelSettings

from smolagents.default_tools import DuckDuckGoSearchTool


@function_tool
def web_search(query: str):
    """
    Performs a duckduckgo web search based on your query (think a Google search) then returns the top search results.

    Args:
        query: The search query to perform.
    """
    ddgs = DuckDuckGoSearchTool(max_results=5)
    results = ddgs(query)
    return results


INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 "
    "words. Capture the main points. Write succinctly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary "
    "itself."
)

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[web_search],
    model_settings=ModelSettings(tool_choice="required"),
)
