"""
SmartWebSearch.__init__
~~~~~~~~~~~~

This module implements the SmartWebSearch package.
"""

# Import the required modules
from SmartWebSearch.TavilySearch import TavilySearch, SearchResultsContainer, _SearchResult, _SearchResults, _PageContent, InactiveError, InvalidParameterError
from SmartWebSearch.RAGTool import RAGTool, _KnowledgeBaseSet, _KnowledgeBase
from SmartWebSearch.Summarizer import Summarizer
from SmartWebSearch.QueryStorm import QueryStorm
from SmartWebSearch.Debugger import DebuggerConfiguration
from SmartWebSearch.KeyCheck import KeyCheck, InvalidKeyError

# Set the debugging mode
DebuggerConfiguration.DEBUGGING = True
DebuggerConfiguration.CREATE_DEBUG_FILES = False
DebuggerConfiguration.SKIP_LOW_IMPORTANCE = True

# Print the version of the package
__version__ = "1.1.1"

# Print the name of the package
__name__ = "SmartWebSearch"

# Print the author of the package
__author__ = "LIN WAI CHON"

# Print the email of the author of the package
__email__ = "jacksonlam.temp@gmail.com"

# Print the license of the package
__license__ = "MIT"

# Print the URL of the package
__url__ = "https://github.com/LittleWai07/smart-web-search-package"

# Print the description of the package
__description__ = "SmartWebSearch is a Python package that combines the Tavily search API with Retrieval-Augmented Generation (RAG), LLM-powered query expansion, and web content extraction to perform intelligent, deep web searches with automated summarization."

# SmartWebSearch class
class SmartWebSearch:
    """
    A class for searching web using Tavily API with built-in RAG (Retrieval-Augmented Generation) capabilities.
    """

    def __init__(self, ts_api_key: str, openai_comp_api_key: str, model: str = "deepseek-chat", openai_comp_api_base_url: str = "https://api.deepseek.com/chat/completions") -> None:
        """
        Initialize the SmartWebSearch object.

        Args:
            ts_api_key (str): The Tavily API key.
            openai_comp_api_key (str): The OpenAI Compatible API key.
            model (str): The model to use.
            openai_comp_api_base_url (str): The OpenAI Compatible API base URL.
            debug (bool): Whether to enable debug mode.

        Returns:
            None
        """

        # Initialize the Tavily API
        self.ts_api_key: str = ts_api_key
        
        # Initialize the essential objects
        self.rag: RAGTool = RAGTool()
        self.smr: Summarizer = Summarizer(openai_comp_api_key, model, openai_comp_api_base_url)
        self.qs: QueryStorm = QueryStorm(openai_comp_api_key, model, openai_comp_api_base_url)

    def change_api_keys(self, ts_api_key: str, openai_comp_api_key: str, model: str = "deepseek-chat", openai_comp_api_base_url: str = "https://api.deepseek.com/chat/completions") -> None:
        """
        Change the API keys of the SmartWebSearch object.

        Args:
            ts_api_key (str): The Tavily API key.
            openai_comp_api_key (str): The OpenAI Compatible API key.
            model (str): The model to use.
            openai_comp_api_base_url (str): The OpenAI Compatible API base URL.

        Returns:
            None
        """

        # Change the API keys
        self.ts_api_key: str = ts_api_key
        self.smr.openai_comp_api_key = openai_comp_api_key
        self.qs.openai_comp_api_key = openai_comp_api_key

        # Change the model
        self.smr.model = model
        self.qs.model = model

        # Change the OpenAI Compatible API base URL
        self.smr.openai_comp_api_base_url = openai_comp_api_base_url
        self.qs.openai_comp_api_base_url = openai_comp_api_base_url

        # Check the OpenAI Compatible API key
        KeyCheck.check_tavily_api_key(ts_api_key)
        KeyCheck.check_openai_comp_api_key(openai_comp_api_key, model, openai_comp_api_base_url)

    def search(self, prompt: str) -> str:
        """
        Perform a normal search using the Tavily API.

        Args:
            prompt (str): The search prompt.

        Returns:
            str: The search results.
        """

        # Create the TavilySearch object
        ts: TavilySearch = TavilySearch(self.ts_api_key)

        # Generate some search queries
        m_query, *a_queries = self.qs.storm_with_prompt(prompt)

        if a_queries:
            # Perform the search
            results: list[_SearchResults] | _SearchResults = ts.search_d(m_query, a_queries, include_main_query = True, include_page_content = False)

            # Concatenate the summaries of the search results
            content = '\n'.join([ result.summary for result in results ])
        else:
            # Perform the search
            results: list[_SearchResults] | _SearchResults = ts.search(m_query, include_page_content = False)

            # Concatenate the summaries of the search results
            content = results.summary

        # Summerize the content
        return self.smr.summarize(prompt, content)
    
    def deepsearch(self, prompt: str) -> str:
        """
        Perform a deep search using the Tavily API.

        Args:
            prompt (str): The search prompt.

        Returns:
            str: The search results.
        """

        # Create the TavilySearch object
        ts: TavilySearch = TavilySearch(self.ts_api_key)

        # Create SearchResultsContainer object
        src: SearchResultsContainer = SearchResultsContainer()

        # Decompose the prompt into tasks
        tasks: list[str] = self.qs.decompose_tasks_with_prompt(prompt)

        # Create a task queries container to store the queries for each task
        """
        task_queries (list)
        - task (list)
            - main_query (str)
            - auxiliary_queries (list[str])
        """

        task_queries: list[list[str, list[str]]] = []

        # Loop through the tasks
        for task in tasks:
            # Generate queries
            aux_queries_list: list[str] = []

            m_query, *a_queries = self.qs.storm_with_prompt(task)
            aux_queries_list.append(a_queries)

            # Search with main query
            results: _SearchResults | list[_SearchResults] = ts.search(m_query, max_results = 15)
            summary = results.summary
            src.append(results)

            if a_queries:
                # Search with auxiliary queries
                results: _SearchResults | list[_SearchResults] = ts.search_d(m_query, a_queries, max_results_for_each = 15)
                src.append(results)

                # Concatenate the summaries of the search results
                for res in results:
                    summary += '\n' + res.summary

            # If the length of the search results content less than 200,000, generate more queries with the summary
            if len(src.to_str(False)) < 200000:
                # Generate queries
                a_queries: list[str] = self.qs.storm_with_summary(task, summary)
                aux_queries_list.append(a_queries)

                # Search with auxiliary queries
                results = ts.search_d(m_query, a_queries)
                src.append(results)

            # Append the task queries
            task_queries.append([m_query, aux_queries_list])

        # Create knowledge base
        kb = src.to_rag(self.rag, False)

        # Match the queries with the knowledge base
        matches = []
        for task in task_queries:
            m_query: str = task[0]
            for a_query in task[1]:
                matches.extend(self.rag.match_knowledge(kb, f"{m_query} {a_query}", top_k = 20, threshold_score = 0.81))

        # Generate conclusion
        conclusion = self.smr.summarize(prompt, "\n".join(src.get_summaries() + [match[1] for match in matches]))

        # Return the conclusion
        return conclusion