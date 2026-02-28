"""
SmartWebSearch.SmartWebSearch
~~~~~~~~~~~~

This module implements the SmartWebSearch.
"""

# Import the required modules
from SmartWebSearch.TavilySearch import TavilySearch, SearchResultsContainer, _SearchResults
from SmartWebSearch.RAGTool import RAGTool
from SmartWebSearch.Summarizer import Summarizer
from SmartWebSearch.QueryStorm import QueryStorm
from SmartWebSearch.KeyCheck import KeyCheck
from SmartWebSearch.Progress import Progress, _ProgressData
from SmartWebSearch.Progress import ProgressStatusSelector as pss
from typing import Callable, Any

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

        # Initialize the Progress object
        self.progress: Progress = Progress()

        # Define a function for listening to the progress updates of RAGTool
        def rag_progress_listener(progress_data: _ProgressData) -> None:
            """
            A function for listening to the progress updates of RAGTool.

            Args:
                progress_data (_ProgressData): The progress data.

            Returns:
                None
            """

            # Update the progress
            match progress_data.status:
                case pss.KL_BASE_CREATING:
                    self.progress._update_progress(pss.KL_BASE_CREATING, progress_data.message, progress_data.data, progress_data.progress)
                case pss.KL_BASE_CREATED:
                    self.progress._update_progress(pss.KL_BASE_CREATED, progress_data.message, progress_data.data, progress_data.progress)
                case pss.KL_BASE_MATCHING:
                    self.progress._update_progress(pss.KL_BASE_MATCHING, progress_data.message, progress_data.data, progress_data.progress)
                case pss.KL_BASE_MATCHED:
                    self.progress._update_progress(pss.KL_BASE_MATCHED, progress_data.message, progress_data.data, progress_data.progress)
                case pss.COMPLETED:
                    self.progress._update_progress(pss.PART_COMPLETED, progress_data.message, progress_data.data, progress_data.progress)

        # Add progress listener to RAGTool
        self.rag.progress.add_progress_listener(rag_progress_listener)

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

    def search(self, prompt: str, stream_cb: Callable[[str], None] = None) -> str:
        """
        Perform a normal search using the Tavily API.

        Args:
            prompt (str): The search prompt.
            stream_cb (Callable[[str], None]) = None: The callback function for stream. If callback function is not None, the response will be streamed to the callback function as parameters.

        Returns:
            str: The search results.
        """

        # Define a function for listening to the progress updates of TavilySearch
        def ts_progress_listener(progress_data: _ProgressData) -> None:
            """
            A function for listening to the progress updates of TavilySearch.

            Args:
                progress_data (_ProgressData): The progress data.

            Returns:
                None
            """

            # Update the progress
            match progress_data.status:
                case pss.SEARCHING:
                    self.progress._update_progress(pss.SEARCHING, progress_data.message, progress_data.data, progress_data.progress)
                case pss.SEARCHED:
                    self.progress._update_progress(pss.SEARCHED, progress_data.message, progress_data.data, progress_data.progress)
                case pss.PARSING:
                    self.progress._update_progress(pss.PARSING, progress_data.message, progress_data.data, progress_data.progress)
                case pss.PARSED:
                    self.progress._update_progress(pss.PARSED, progress_data.message, progress_data.data, progress_data.progress)
                case pss.PART_COMPLETED:
                    self.progress._update_progress(pss.PART_COMPLETED, progress_data.message, progress_data.data, progress_data.progress)
                case pss.COMPLETED:
                    self.progress._update_progress(pss.PART_COMPLETED, progress_data.message, progress_data.data, progress_data.progress)

        # Create the TavilySearch object
        ts: TavilySearch = TavilySearch(self.ts_api_key)

        # Add progress listener to TavilySearch
        ts.progress.add_progress_listener(ts_progress_listener)

        # Update progress
        self.progress._update_progress(pss.STORMING, f"Storming the main queries and auxiliary queries for the prompt '{prompt}'")

        # Generate some search queries
        m_query, *a_queries = self.qs.storm_with_prompt(prompt)

        # Update progress
        self.progress._update_progress(pss.STORMED, f"Stormed the main queries and auxiliary queries for the prompt '{prompt}'", {
            'main_query': m_query,
            'auxiliary_queries': a_queries
        })

        if a_queries:
            # Perform the search
            results: list[_SearchResults] = ts.search_d(m_query, a_queries, include_main_query = True, include_page_content = False)

        else:
            # Perform the search
            results: list[_SearchResults] = [ts.search(m_query, include_page_content = False)]

        # Concatenate the summaries of the search results
        content: str = '\n'.join([ result.summary for result in results ])

        # Update progress
        self.progress._update_progress(pss.CONCLUDING, f"Concluding the content for the prompt '{prompt}'")

        # Summarize the content
        conclusion = self.smr.summarize(prompt, content, stream_cb)

        # Update progress
        self.progress._update_progress(pss.CONCLUDED, f"Concluded the content for the prompt '{prompt}'", {
            'prompt': prompt,
            'summaries': [ result.summary for result in results ],
            'conclusion': conclusion
        })

        self.progress._update_progress(pss.COMPLETED, f"Search completed for the prompt '{prompt}'", {
            'prompt': prompt,
            'summaries': [ result.summary for result in results ],
            'conclusion': conclusion
        })

        self.progress._update_progress(pss.IDLE)

        # Summerize the content
        return conclusion
    
    def deepsearch(self, prompt: str, stream_cb: Callable[[str], None] = None) -> str:
        """
        Perform a deep search using the Tavily API.

        Args:
            prompt (str): The search prompt.
            stream_cb (Callable[[str], None]) = None: The callback function for stream. If callback function is not None, the response will be streamed to the callback function as parameters.

        Returns:
            str: The search results.
        """

        # Define a function for listening to the progress updates of TavilySearch
        def ts_progress_listener(progress_data: _ProgressData) -> None:
            """
            A function for listening to the progress updates of TavilySearch.

            Args:
                progress_data (_ProgressData): The progress data.

            Returns:
                None
            """

            # Update the progress
            match progress_data.status:
                case pss.SEARCHING:
                    self.progress._update_progress(pss.SEARCHING, progress_data.message, progress_data.data, progress_data.progress)
                case pss.SEARCHED:
                    self.progress._update_progress(pss.SEARCHED, progress_data.message, progress_data.data, progress_data.progress)
                case pss.PARSING:
                    self.progress._update_progress(pss.PARSING, progress_data.message, progress_data.data, progress_data.progress)
                case pss.PARSED:
                    self.progress._update_progress(pss.PARSED, progress_data.message, progress_data.data, progress_data.progress)
                case pss.PART_COMPLETED:
                    self.progress._update_progress(pss.PART_COMPLETED, progress_data.message, progress_data.data, progress_data.progress)
                case pss.COMPLETED:
                    self.progress._update_progress(pss.PART_COMPLETED, progress_data.message, progress_data.data, progress_data.progress)

        # Create the TavilySearch object
        ts: TavilySearch = TavilySearch(self.ts_api_key)

        # Add progress listener to TavilySearch
        ts.progress.add_progress_listener(ts_progress_listener)

        # Create SearchResultsContainer object
        src: SearchResultsContainer = SearchResultsContainer()

        # Update progress
        self.progress._update_progress(pss.STORMING, f"Decomposing the prompt '{prompt}' into tasks")

        # Decompose the prompt into tasks
        tasks: list[str] = self.qs.decompose_tasks_with_prompt(prompt)

        # Update progress
        self.progress._update_progress(pss.STORMED, f"Decomposed the prompt '{prompt}' into tasks", {
            'tasks': tasks
        })

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
            # Update progress
            self.progress._update_progress(pss.STORMING, f"Storming the main queries and auxiliary queries for the task '{task}'")

            # Generate queries
            aux_queries_list: list[str] = []

            m_query, *a_queries = self.qs.storm_with_prompt(task)
            aux_queries_list.append(a_queries)

            # Update progress
            self.progress._update_progress(pss.STORMED, f"Stormed the main queries and auxiliary queries for the task '{task}'", {
                'main_query': m_query,
                'auxiliary_queries': a_queries
            })

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

            # If the length of the search results content less than 600,000, generate more queries with the summary
            if len(src.to_str(False)) < 600000:
                # Generate queries
                a_queries: list[str] = self.qs.storm_with_summary(task, summary)
                aux_queries_list.append(a_queries)

                # Search with auxiliary queries
                results = ts.search_d(m_query, a_queries, max_results_for_each = 10)
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
                matches.extend(self.rag.match_knowledge(kb, f"{m_query} {a_query}", top_k = 10, threshold_score = 0.81))

        # Update progress
        self.progress._update_progress(pss.CONCLUDING, f"Concluding the summaries and matches for the prompt '{prompt}'", {
            'prompt': prompt,
            'summaries': src.get_summaries(),
            'matches': matches,
        })

        # Generate conclusion
        conclusion = self.smr.summarize(prompt, "\n".join(src.get_summaries() + [match[1] for match in matches]), stream_cb)

        # Update progress
        self.progress._update_progress(pss.CONCLUDED, f"Concluded the summaries and matches for the prompt '{prompt}'", {
            'prompt': prompt,
            'summaries': src.get_summaries(),
            'matches': matches,
            'conclusion': conclusion
        })

        self.progress._update_progress(pss.COMPLETED, f"Search completed for the prompt '{prompt}'", {
            'prompt': prompt,
            'summaries': src.get_summaries(),
            'matches': matches,
            'conclusion': conclusion
        })

        self.progress._update_progress(pss.IDLE)

        # Return the conclusion
        return conclusion