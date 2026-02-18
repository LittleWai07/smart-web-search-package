"""
SmartWebSearch
~~~~~~~~~~~~

An example of how to use the SmartWebSearch package.
"""

# Import the SmartWebSearch module
import SmartWebSearch as sws

# Create a SmartWebSearch object
search = sws.SmartWebSearch("<Tavily API Key>", "<OpenAI Compatible API Key>", "<AI Model>", "<OpenAI Compatible API Base URL>")

# Search for a prompt
print(search.search(input("Enter a prompt: ")))

# Deep search for a prompt
print(search.deepsearch(input("Enter a prompt: ")))