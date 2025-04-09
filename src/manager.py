import asyncio
import os
import time
import aiofiles
import datetime

from agents import Runner, custom_span, gen_trace_id, trace
from dotenv import load_dotenv
from rich.console import Console

from deep_research.agents.planner_agent import (
    WebSearchItem,
    WebSearchPlan,
    planner_agent,
)
from deep_research.agents.query_reformulation_agent import query_reformulation_agent
from deep_research.agents.search_agent import (
    search_agent,
    search_output_validation_agent,
)
from deep_research.agents.writer_agent import ReportData, writer_agent
from utils.printer import Printer

load_dotenv()


class ResearchManager:
    def __init__(self):
        self.console = Console()
        self.printer = Printer(self.console)
        self.trace_id = gen_trace_id()

        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d-%H-%M-%S")

        # Create results directory with timestamp prefix
        self.results_dir = os.path.join("results", f"{timestamp}_{self.trace_id}")
        os.makedirs(self.results_dir, exist_ok=True)

        # Create dedicated search results directory
        self.search_results_dir = os.path.join(self.results_dir, "searches")
        os.makedirs(self.search_results_dir, exist_ok=True)

    async def run(self, query: str) -> None:
        with trace("Research trace", trace_id=self.trace_id):
            self.printer.update_item(
                "trace_id",
                f"View trace: https://platform.openai.com/traces/trace?trace_id={self.trace_id}",
                is_done=True,
                hide_checkmark=True,
            )

            self.printer.update_item(
                "starting",
                "Starting research...",
                is_done=True,
                hide_checkmark=True,
            )

            reformulated_query: str = await self._query_reformulation(query)
            search_plan: WebSearchPlan = await self._plan_searches(reformulated_query)
            search_results: list[str] = await self._perform_searches(search_plan)
            report: ReportData = await self._write_report(
                reformulated_query, search_results
            )

            self.printer.update_item(
                "saving", "Saving final report and follow-up questions..."
            )
            await self._save_final_report(report)
            self.printer.mark_item_done("saving")

            final_report = f"Report summary\n\n{report.short_summary}"
            self.printer.update_item("final_report", final_report, is_done=True)
            self.printer.end()

        print("\n\n=====REPORT=====\n\n")
        print(f"Report: {report.markdown_report}")
        print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
        follow_up_questions = "\n".join(report.follow_up_questions)
        print(f"Follow up questions: {follow_up_questions}")

    async def _query_reformulation(self, query: str) -> str:
        self.printer.update_item(
            "query_reformulation", f"Reformulating the query: {query}."
        )
        result = await Runner.run(
            query_reformulation_agent,
            f"Query: {query}",
        )

        self.printer.update_item(
            "query_reformulation",
            f"Reformulated query: {result.final_output.query}",
            is_done=True,
        )
        return result.final_output.query

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        self.printer.update_item("planning", "Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        self.printer.update_item(
            "planning",
            f"Will perform {len(result.final_output.searches)} searches",
            is_done=True,
        )
        return result.final_output_as(WebSearchPlan)

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        with custom_span("Search the web"):
            self.printer.update_item("searching", "Searching...")
            num_completed = 0
            tasks = [
                asyncio.create_task(self._search(item)) for item in search_plan.searches
            ]
            results = []
            for i, task in enumerate(asyncio.as_completed(tasks)):
                result = await task
                if result is not None:
                    results.append(result)
                    await self._save_search_result(i, result)
                num_completed += 1
                self.printer.update_item(
                    "searching", f"Searching... {num_completed}/{len(tasks)} completed"
                )
            self.printer.mark_item_done("searching")
            return results

    async def _search(self, item: WebSearchItem) -> str | None:
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )

            # Agent for the validation whether search results were successful.
            # Unfortunately due to rate limits of Duck Duck Go results are limited.
            # Search agent hallucinations then and we want to avoid that.
            validation = await Runner.run(
                search_output_validation_agent, result.final_output
            )

            if not validation.final_output.successful_search:
                print("The search results were unsuccessful.")
                return None
            return str(result.final_output)

        except Exception:
            return None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        self.printer.update_item("writing", "Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = Runner.run_streamed(
            writer_agent,
            input,
        )
        update_messages = [
            "Thinking about report...",
            "Planning report structure...",
            "Writing outline...",
            "Creating sections...",
            "Cleaning up formatting...",
            "Finalizing report...",
            "Finishing report...",
        ]

        last_update = time.time()
        next_message = 0
        async for _ in result.stream_events():
            if time.time() - last_update > 5 and next_message < len(update_messages):
                self.printer.update_item("writing", update_messages[next_message])
                next_message += 1
                last_update = time.time()

        self.printer.mark_item_done("writing")
        return result.final_output_as(ReportData)

    async def _save_search_result(self, index: int, result: str) -> None:
        """Save a search result to a file in the search results directory asynchronously."""
        filename = os.path.join(self.search_results_dir, f"search_result_{index}.txt")
        async with aiofiles.open(filename, "w", encoding="utf-8") as f:
            await f.write(result)

    async def _save_final_report(self, report: ReportData) -> None:
        """Save the final report to a file in the results directory asynchronously."""
        # Save markdown report
        report_path = os.path.join(self.results_dir, "final_report.md")
        async with aiofiles.open(report_path, "w", encoding="utf-8") as f:
            await f.write(report.markdown_report)

        # Save follow-up questions
        questions_path = os.path.join(self.results_dir, "follow_up_questions.txt")
        async with aiofiles.open(questions_path, "w", encoding="utf-8") as f:
            await f.write("\n".join(report.follow_up_questions))

        self.printer.update_item(
            "saving",
            f"Report saved to: {report_path}\nFollow-up questions saved to: {questions_path}",
            is_done=True,
        )

        print(f"\nReport saved to: {report_path}")
        print(f"Follow-up questions saved to: {questions_path}")
