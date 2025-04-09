import asyncio

from src.manager import ResearchManager


async def main() -> None:
    query = input("Q: What would you like to research?\nA: ")
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(main())
