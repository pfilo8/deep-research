from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from typing import Optional

from agents import Agent, function_tool
from agents.model_settings import ModelSettings


def extract_page_content(url: str) -> Optional[str]:
    """
    Extracts the main content from a web page.

    Args:
        url: The URL of the page to extract content from.

    Returns:
        The extracted text content or None if extraction fails.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading and trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = " ".join(chunk for chunk in chunks if chunk)

        return text
    except Exception as e:
        print(f"Error extracting content from {url}: {str(e)}")
        return None


@function_tool
def web_search(query: str) -> str:
    """
    Performs a duckduckgo web search based on your query (think a Google search) then returns the top search results
    and attempts to extract content from the first result.

    Args:
        query: The search query to perform.
    """
    ddgs = DDGS()
    results = ddgs.text(query, max_results=1)
    if len(results) == 0:
        raise Exception("No results found! Try a less restrictive/shorter query.")

    result = results[0]
    page_content = extract_page_content(result["href"])

    postprocessed_result = f"[{result['title']}]({result['href']})\n{result['body']}"

    if page_content:
        postprocessed_result += f"\n\n## Page Content\n\n{page_content}"

    return "## Search Results\n\n" + postprocessed_result


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
