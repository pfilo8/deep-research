# Deep Research

An intelligent research assistant powered by OpenAI's Agent framework that helps conduct deep, comprehensive research on any topic.

## Overview

Deep Research is a Python-based tool that leverages AI to perform thorough research on any given query. It uses a multi-agent system to reformulate queries, plan research strategies, perform web searches, and generate detailed reports with follow-up questions.

## Features

- 🤖 **Intelligent Query Reformulation**: Automatically improves and expands your research questions
- 🔍 **Strategic Web Search**: Plans and executes multiple targeted searches
- 📝 **Comprehensive Reports**: Generates well-structured research reports
- 🔄 **Follow-up Questions**: Suggests relevant follow-up questions for deeper research
- 📊 **OpenAI Trace Integration**: Full transparency with OpenAI's trace visualization

## Prerequisites

- Python 3.11 or higher
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/deep-research.git
cd deep-research
```

2. Install [uv](https://github.com/astral-sh/uv):
```bash
pip install uv
```

3. Install dependencies with uv:
```bash
uv pip install -r requirements.txt
```

4. Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your_api_key_here  # On Unix/macOS
# or
set OPENAI_API_KEY=your_api_key_here     # On Windows
```

## Usage

```bash
uv run main.py
```

When prompted, enter your research question. The tool will:
1. Reformulate your query for optimal results
2. Plan a comprehensive search strategy
3. Execute multiple targeted web searches
4. Generate a detailed research report
5. Provide follow-up questions for further exploration

Results are saved in the `results/` directory with a unique trace ID for each session.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
