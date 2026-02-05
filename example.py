"""
SmartWebSearch
~~~~~~~~~~~~

An example of how to use the SmartWebSearch package.
"""

# Import the required modules
from SmartWebSearch.TavilySearch import TavilySearch
from SmartWebSearch.RAGTool import RAGTool
from SmartWebSearch.Debugger import DebuggerConfiguration
import json, requests

# Enable debugging
DebuggerConfiguration.DEBUGGING = True

# Get user input
query = input("Enter a query for search on web: ")

# Search for the query
results = TavilySearch("<TAVILY_API_KEY>").search(query)

# Concatenate the search results as content
content_data = results.summary
for result in results.results:
    content_data += "\n" + result.title + "\n" + result.page_content.content

# Print the length of the content
print("Content length:", len(content_data))

# Build the knowledge base
rag = RAGTool()

# Build the knowledge base
kb = rag.build_knowledge(content_data)

# Match the knowledge base with the query
while True:
    # Get user input
    query = input("Enter a query for search on knowledge base: ")

    # Match the knowledge base with the query
    matches = rag.match_knowledge(kb, query, threshold_score = 6.0)

    # If no matches, try again with a lower threshold
    if not matches:
        matches = rag.match_knowledge(kb, query, threshold_score = 4.0)

    # If no matches, return no matches
    if not matches:
        print("No matches found")
        continue

    # Print the count of the matches
    print("Matches count:", len(matches))

    # Concatenate the matches as matched_content
    matched_content = ""
    for match in matches:
        if not match[1]: continue
        matched_content += "\n" + match[1]

    # Send the matched_content to the DeepSeek API for conclusion
    res = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer <DEEPSEEK_API_KEY>"
        },
        json = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": f"Summarize the following text according to the web search query in detailed: \nQuery: {query}\nText: {matched_content if matched_content != '' else 'No matches found'}"
                }
            ]
        }
    )

    # Print the conclusion
    print(json.loads(res.text)["choices"][0]["message"]["content"])