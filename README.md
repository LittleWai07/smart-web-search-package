# Smart Web Search Package

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

SmartWebSearch is a Python package that combines the Tavily search API with Retrieval-Augmented Generation (RAG), LLM-powered query expansion, and web content extraction to perform intelligent, deep web searches with automated summarization.

## Package Latest Version
- 1.3.5

## Features
- 🌐 **Web Search** – Uses Tavily API to fetch relevant search results.
- 🧠 **Query Expansion** – Leverages LLMs (e.g., DeepSeek) to decompose complex queries and generate auxiliary searches.
- 📄 **Content Extraction** – Fetches full page content using headless Chrome and filters noise.
- 🔍 **RAG Pipeline** – Embeds documents with multilingual models (e.g., multilingual-e5-base) and retrieves context-aware chunks.
- 📝 **Summarization** – Summarizes retrieved content using LLMs.

## Environment
- **Python 3.12 or above**
- **Windows 11 Pro 64-bit** (macOS haven't tested)
- **Python Packages** (requests, bs4, selenium, markdownify, tavily, numpy, sentence_transformers, langchain_text_splitters)

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
    print(token, end='', flush=True)

# --------------------------------------------------------------------
# Run a search
# --------------------------------------------------------------------
prompt = input("Enter a prompt: ")

print("=== Normal Search (Tavily summaries) ===")
search.search(prompt, stream_summary_callback)

print("\n=== Deep Search (full page content + RAG) ===")
search.deepsearch(prompt, stream_summary_callback)
```

**Note**: The documentation of this package will be completed in the future.

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/LittleWai07/smart-web-search-package/blob/main/LICENSE) file for details