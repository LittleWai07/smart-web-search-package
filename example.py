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