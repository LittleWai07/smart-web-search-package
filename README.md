# Smart Web Search Package

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/SmartWebSearch)](https://pypi.org/project/SmartWebSearch/)

## Table of Contents

- [Introduction](#introduction)
- [Package Latest Version](#package-latest-version)
- [Features](#features)
- [Environment](#environment)
- [Installation](#installation)
- [API Keys](#api-keys)
- [Quick Start](#quick-start)
- [Search v.s. DeepSearch](#search-vs-deepsearch)
- [License](#license)

## Introduction

SmartWebSearch is a Python package that combines the Tavily search API with Retrieval-Augmented Generation (RAG), LLM-powered query expansion, and web content extraction to perform intelligent, deep web searches with automated summarization.

## Package Latest Version
- 1.6.1

## Features
- 🌐 **Web Search** – Uses Tavily API to fetch relevant search results.
- 🧠 **Query Expansion** – Leverages LLMs (e.g., DeepSeek) to decompose complex queries and generate auxiliary searches.
- 📄 **Content Extraction** – Fetches full page content using headless Chrome and filters noise.
- 🔍 **RAG Pipeline** – Embeds documents with multilingual models (e.g., multilingual-e5-base) and retrieves context-aware chunks.
- 📝 **Summarization** – Summarizes retrieved content using LLMs.

## Environment
- **Python 3.12 or above**
- **Latest Version of Google Chrome**
- **Windows 11 / macOS 15 Sequoia (Apple Silicon chips (M-series) are required for supporting PyTorch 2.4.0 or above) or above**
- **Python Packages** (requests, bs4, selenium, markdownify, tavily, numpy, sentence_transformers, langchain_text_splitters, rich, art, langdetect)

## Installation

### Method 1

- **PYPI**: Install the SmartWebSearch package from PYPI through command `pip install smartwebsearch`

### Method 2

- **The SmartWebSearch Package**: Install the SmartWebSearch package [here](https://github.com/LittleWai07/smart-web-search-package/archive/refs/heads/main.zip) or with git command `git clone https://github.com/LittleWai07/smart-web-search-package.git` (Git is required to run this command)
- **Required Python Packages**: Install the required Python packages by command `pip install -r requirements.txt`

## API Keys
You need two API keys
- **Tavily API key**: Sign up and get the API key [here](https://www.tavily.com) (1,000 free quotas per month)
- **OpenAI Compatible API key**: eg., from [OpenAI](https://platform.openai.com/), [DeepSeek](https://platform.deepseek.com/), etc.

**Note**: Thinking model is **not recommended** to use due to the running efficiency.

## 🔒 Security Note

For security reasons, **never hard-code your API keys directly in your source code**. 
Instead, store them in environment variables, a `.env` file or a `*.json` file and load them into your program.

## Quick Start
Fill in the API keys and following required parameters manually.
- **Tavily API Key**: The Tavily search API key (The key starts with `tvly-dev-`).
- **OpenAI Compatible API Key**: The API key for the OpenAI Compatible API platform (The key usually starts with `sk-`).
- **AI Model**: The id of the AI model used for summarization. (Default: `deepseek-chat`)
- **OpenAI Compatible API Base URL**: The base url of the OpenAI Compatible API platform (The URL usually end with `/chat/completions`) (Default: `https://api.deepseek.com/chat/completions`)

```python
"""
SmartWebSearch
~~~~~~~~~~~~
An example of how to use the SmartWebSearch package.
"""

# Import the SmartWebSearch package
import SmartWebSearch as sws

# --------------------------------------------------------------------
# You can configure for different API providers by changing the 
# model and base_url. Below are some examples:
# --------------------------------------------------------------------

# Example 1: Using DeepSeek (default)
search: sws.SmartWebSearch = sws.SmartWebSearch(
    "<Tavily API Key>",
    sws.AIModel(
        "<OpenAI Compatible API Key>",
        model="deepseek-chat",
        openai_comp_api_base_url="https://api.deepseek.com/chat/completions"
    )
)

# Example 2: Using OpenAI
# search: sws.SmartWebSearch = sws.SmartWebSearch(
#     "<Tavily API Key>",
#     sws.AIModel(
#         "<OpenAI Compatible API Key>",
#         model="gpt-4-turbo-preview",
#         openai_comp_api_base_url="https://api.openai.com/v1/chat/completions"
#     )
# )

# --------------------------------------------------------------------
# Define a callback function for streaming the summary results
# --------------------------------------------------------------------
def stream_summary_callback(token: str):
    if token == sws.Summarizer.COMPLETION_ENDED:
        # Add a new line after the completion ended to separate the summaries and the debugging messages
        print()
        return

    print(token, end='', flush=True)

# --------------------------------------------------------------------
# Run a search
# --------------------------------------------------------------------
prompt = input("Enter a prompt: ")

print("=== Normal Search (Tavily summaries) ===")
search.search(prompt, stream_summary_callback)

print("\n=== Deep Search (full page content + RAG) ===")
search.deepsearch(prompt, stream_summary_callback, depth = 'HIGH') # You can set the search depth here with ('MINIMAL', 'LOW', 'MEDIUM', 'HIGH')
```

## SmartWebSearch CLI Tool (New feature in SmartWebSearch v1.6.0)

You can use the SmartWebSearch CLI tool to run a search or deep search.

After you install the SmartWebSearch package by command `pip install smartwebsearch`, you can run the CLI tool by command `sws-cli`.

Follow the instructions on the screen to set up your API keys, then you can start using the CLI tool to search.

**Note**: There is **no context memory** in the CLI tool, every search is independent.

### Commands & Usages
**Note**: `<> = Required, [] = Optional, () = Available Options`

- `> <prompt>`: Start a new search in current search mode with the given prompt
- `> /help`: Show the help message
- `> /search`: Switch to search mode
- `> /deepsearch [depth (MINIMAL, LOW, MEDIUM, HIGH)]`: Switch to deep search mode with the given depth
- `> /reset`: Reset the CLI configuration and API credentials
- `> /save`: Save the messages to a file (JSON)
- `> /cls`: Clear the console
- `> /clear`: Clear the console
- `> /exit`: Exit the program

## Search v.s. DeepSearch

### Search

1. **Brainstorm Queries**: Brainstorm the search queries according to your prompt with AI model. Including a main search query and not more than 5 auxiliary queries.
2. **The 1st-Term Search**: The first term of web searching. Use the main search query to search first, then use the main search query with each auxiliary query as matches to search. After that, Grab all the summaries from the search results.
3. **Final Conclusion**: Do a final conclusion with the summaries with AI model.

### DeepSearch

1. **Decompose Tasks**: Decompose the prompt into search tasks so as to allow multiple main queries in the same search.
2. **Brainstorm Queries**: Brainstorm the search queries for each task with AI model. Each task includes a main search query and not more than 5 auxiliary queries.
3. **The 1st-Term Search**: The first term of web searching. Use the main search query to search first, then use the main search query with each auxiliary query as matches to search. After that, Fetch all the page contents and grab all the summaries from the search results. This process is repeated for each task.
4. **Brainstorm Extra Auxiliary Queries**: Brainstorm the extra queries for each task with AI model. Each task includes not more than 12 extra auxiliary queries (According to the search depth). (This step will be skipped if the search depth is set to 'MINIMAL')
5. **The 2nd-Term Search**: Use the main search query with each extra auxiliary query as matches to search. After that, Fetch all the page contents and grab all the summaries from the search results. This process is repeated for each task. (This step will be skipped if the search depth is set to 'MINIMAL')
6. **RAG Pipeline**: Embed the page contents with multilingual models (e.g., multilingual-e5-base) and retrieve context-aware chunks.
7. **Final Conclusion**: Do a final conclusion with all summaries and RAG matches with AI model.

### Differences Between Each Search Depth (Only For DeepSearch):

- **MINIMAL**: Skip the extra auxiliary queries brainstorm and 2nd-Term Search, and maximum content length for each page is limited to 80,000 characters.
- **LOW**: Maximum extra auxiliary queries to brainstorm is 3, and maximum content length for each page is limited to 120,000 characters.
- **MEDIUM**: Maximum extra auxiliary queries to brainstorm is 5, and maximum content length for each page is limited to 150,000 characters.
- **HIGH**: Maximum extra auxiliary queries to brainstorm is 12, and maximum content length for each page is limited to 180,000 characters.

### Table comparison

| Comparison | Search | DeepSearch (MINIMAL) | DeepSearch (LOW) | DeepSearch (MEDIUM) | DeepSearch (HIGH) |
| -------- | ------- | ------- | ------- | ------- | ------- |
| Decompose Tasks | ❌ | ✅ | ✅ | ✅ | ✅ |
| Brainstorm Queries | ✅ (Maximum **5 queries**) | ✅ (Maximum **5 queries**) | ✅ (Maximum **5 queries**) | ✅ (Maximum **5 queries**) | ✅ (Maximum **5 queries**) |
| The 1st-Term Search | ✅ (Grab **summaries** only) | ✅ (Grab **summaries** and fetch **page contents** with **80k chars** maximum content for each page) | ✅ (Grab **summaries** and fetch **page contents** with **120k chars** maximum content for each page) | ✅ (Grab **summaries** and fetch **page contents** with **150k chars** maximum content for each page) | ✅ (Grab **summaries** and fetch **page contents** with **180k chars** maximum content for each page) |
| Brainstorm Extra Auxiliary Queries | ❌ | ❌ | ✅ (Maximum **3 extra auxiliary queries**) | ✅ (Maximum **5 extra auxiliary queries**) | ✅ (Maximum **12 extra auxiliary queries**) |
| The 2nd-Term Search | ❌ | ❌ | ✅ | ✅ | ✅ |
| RAG Pipeline | ❌ | ✅ | ✅ | ✅ | ✅ |
| Final Conclusion | ✅ (Conclude **summaries**) | ✅ (Conclude **summaries** and **RAG matches**) | ✅ (Conclude **summaries** and **RAG matches**) | ✅ (Conclude **summaries** and **RAG matches**) | ✅ (Conclude **summaries** and **RAG matches**) |


**Note**: Detailed API documentation is under development. For now, please refer to the source code and docstrings.

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/LittleWai07/smart-web-search-package/blob/main/LICENSE) file for details