"""
SmartWebSearch.SmartWebSearch
~~~~~~~~~~~~

This module implements the SmartWebSearch.
"""

# Import the required modules
from SmartWebSearch.TavilySearch import TavilySearch, SearchResultsContainer, _SearchResults
from SmartWebSearch.RAGTool import RAGTool, _KnowledgeBaseSet
from SmartWebSearch.Summarizer import Summarizer
from SmartWebSearch.QueryStorm import QueryStorm
from SmartWebSearch.KeyCheck import KeyCheck
from SmartWebSearch.Progress import Progress, _ProgressData
from SmartWebSearch.Progress import ProgressStatusSelector as pss
from SmartWebSearch.AIModel import AIModel
from SmartWebSearch.Debugger import show_debug
from typing import Callable, Any, Literal, TypeAlias
import os
import json
from pathlib import Path

# SmartWebSearch class
class SmartWebSearch:
    """
    A class for searching web using Tavily API with built-in RAG (Retrieval-Augmented Generation) capabilities.
    """

    # Constants
    SEARCH_DEPTH: TypeAlias = Literal['MINIMAL', 'LOW', 'MEDIUM', 'HIGH']

    @staticmethod
    def from_f(config_file_path: str, **kwargs: dict[str, Any]) -> "SmartWebSearch":
        """
        Create a SmartWebSearch object from a credentials configuration file.

        Args:
            config_file_path (str): The path to the credentials configuration file.
            **kwargs (dict[str, Any]): Additional keyword arguments in the request body of the AI model.

        Returns:
            SmartWebSearch: The created SmartWebSearch object.
        """

        # Load the configuration file
        with open(config_file_path, "r", encoding = "utf-8") as f:
            config: dict[str, Any] = json.load(f)

        # Create the SmartWebSearch object
        return SmartWebSearch(
            ts_api_key = config["api_credentials"]["tavily_api_key"],
            ai_model = AIModel(
                openai_comp_api_key = config["api_credentials"]["openai_comp_api_key"],
                openai_comp_api_base_url = config["api_credentials"]["openai_comp_api_base_url"],
                model = config["api_credentials"]["openai_comp_api_model"],
                **kwargs
            )
        )

    def __init__(self, ts_api_key: str, ai_model: AIModel) -> None:
        """
        Initialize the SmartWebSearch object.

        Args:
            ts_api_key (str): The Tavily API key.
            ai_model (AIModel): The AIModel object.

        Returns:
            None
        """

        # Initialize the Tavily API
        self.ts_api_key: str = ts_api_key
        self.ai_model: AIModel = ai_model
        
        # Initialize the essential objects
        self.rag: RAGTool = RAGTool()
        self.smr: Summarizer = Summarizer(ai_model)
        self.qs: QueryStorm = QueryStorm(ai_model)

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

    def change_tavily_api_key(self, ts_api_key: str) -> None:
        """
        Change the API keys of the SmartWebSearch object.

        Args:
            ts_api_key (str): The Tavily API key.

        Returns:
            None
        """

        # Change the API keys
        self.ts_api_key: str = ts_api_key

        # Check the OpenAI Compatible API key
        KeyCheck.check_tavily_api_key(ts_api_key)

    def search(self, prompt: str, stream_cb: Callable[[str], None] = None) -> str:
        """
        Perform a normal search using the Tavily API.

        Args:
            prompt (str): The search prompt.
            stream_cb (Callable[[str], None]) = None: The callback function for stream. If callback function is not None, the response will be streamed to the callback function as parameters.
            kb_output_path (str) = None: The path to the knowledge base output file.

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
        self.progress._update_progress(pss.STORMING, f"Storming the main query and auxiliary queries for the prompt '{prompt}'")

        show_debug(f"Storming the main queries and auxiliary queries for the prompt '{prompt}'")

        # Generate some search queries
        m_query, *a_queries = self.qs.storm_with_prompt(prompt)

        # Update progress
        self.progress._update_progress(pss.STORMED, f"Stormed the main query and {len(a_queries)} auxiliary queries for the prompt '{prompt}'", {
            'main_query': m_query,
            'auxiliary_queries': a_queries
        })

        show_debug(f"Stormed the main queries and {len(a_queries)} auxiliary queries for the prompt '{prompt}'")

        if a_queries:
            # Perform the search
            results: list[_SearchResults] = ts.search_d(m_query, a_queries, include_main_query = True, include_page_content = False)

        else:
            # Perform the search
            results: list[_SearchResults] = [ts.search(m_query, include_page_content = False)]

        # Concatenate the summaries of the search results
        content: str = '\n'.join([ result.summary for result in results ])

        # Final conclusion

        # Update progress
        self.progress._update_progress(pss.FINAL_CONCLUDING, f"Concluding the content for the prompt '{prompt}'")

        show_debug(f"Concluding the content for the prompt '{prompt}'")

        # Summarize the content
        conclusion = self.smr.summarize(prompt, content, stream_cb)

        # Update progress
        self.progress._update_progress(pss.FINAL_CONCLUDED, f"Concluded the content for the prompt '{prompt}'", {
            'prompt': prompt,
            'summaries': [ result.summary for result in results ],
            'conclusion': conclusion
        })

        show_debug(f"Concluded the content for the prompt '{prompt}'")

        self.progress._update_progress(pss.COMPLETED, f"Search completed for the prompt '{prompt}'", {
            'prompt': prompt,
            'summaries': [ result.summary for result in results ],
            'conclusion': conclusion,
            'sources': [ (s_result.title, s_result.snippet, s_result.url) for s_results in results for s_result in s_results.results if not s_result.page_content ]
        })

        show_debug(f"Search completed for the prompt '{prompt}'")

        self.progress._update_progress(pss.IDLE)

        # Summerize the content
        return conclusion
    
    def deepsearch(self, prompt: str, stream_cb: Callable[[str], None] = None, depth: SEARCH_DEPTH = 'MEDIUM') -> str:
        """
        Perform a deep search using the Tavily API.

        Args:
            prompt (str): The search prompt.
            stream_cb (Callable[[str], None]) = None: The callback function for stream. If callback function is not None, the response will be streamed to the callback function as parameters.
            depth (SEARCH_DEPTH) = 'MEDIUM': The depth of the search.

        Returns:
            str: The search results.
        """

        # Set the max content length according to the search depth
        match depth:
            case 'MINIMAL':
                max_content_length: int = 80000
            case 'LOW':
                max_content_length: int = 120000
            case 'MEDIUM':
                max_content_length: int = 150000
            case 'HIGH':
                max_content_length: int = 180000

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

        # Create task conclusions list
        task_conclusions: list[str] = []

        # Create sources list
        sources: list[tuple[str, str, str]] = []

        # Update progress
        self.progress._update_progress(pss.STORMING, f"Decomposing the prompt '{prompt}' into tasks")

        show_debug(f"Decomposing the prompt '{prompt}' into tasks")

        # Decompose the prompt into tasks
        tasks: list[str] = self.qs.decompose_tasks_with_prompt(prompt)

        # Update progress
        self.progress._update_progress(pss.STORMED, f"Decomposed the prompt '{prompt}' into {len(tasks)} tasks", {
            'tasks': tasks
        })

        show_debug(f"Decomposed the prompt '{prompt}' into {len(tasks)} tasks ({', '.join(tasks)})")

        # Loop through the tasks
        for task in tasks:
            # Create SearchResultsContainer object
            src: SearchResultsContainer = SearchResultsContainer()

            # Update progress
            self.progress._update_progress(pss.STORMING, f"Storming the main queries and auxiliary queries for the task '{task}'")

            show_debug(f"Storming the main queries and auxiliary queries for the task '{task}'")

            # Generate queries
            aux_queries_list: list[str] = []
            m_query, *a_queries = self.qs.storm_with_prompt(task)

            # Add the auxiliary queries to the list
            aux_queries_list.extend(a_queries)

            # Update progress
            self.progress._update_progress(pss.STORMED, f"Stormed the main queries and {len(a_queries)} auxiliary queries for the task '{task}'", {
                'main_query': m_query,
                'auxiliary_queries': a_queries
            })

            show_debug(f"Stormed the main queries and {len(a_queries)} auxiliary queries for the task '{task}'")

            # Search with main query
            results: _SearchResults | list[_SearchResults] = ts.search(m_query, max_results = 15, max_content_length = max_content_length)
            summary = results.summary
            src.append(results)

            if a_queries:
                # Search with auxiliary queries
                results: _SearchResults | list[_SearchResults] = ts.search_d(m_query, a_queries, max_results_for_each = 15, max_content_length = max_content_length)
                src.append(results)

                # Concatenate the summaries of the search results
                for res in results:
                    summary += '\n' + res.summary

            # If the search depth is not 'MINIMAL', generate more queries with the summary
            if depth != 'MINIMAL':
                # Update progress
                self.progress._update_progress(pss.STORMING, f"Storming extra auxiliary queries for the task '{task}'")

                show_debug(f"Storming extra auxiliary queries for the task '{task}'")

                # Generate queries
                a_queries: list[str] = self.qs.storm_with_summary(m_query, task, summary)

                # Check the search depth and limit the number of auxiliary queries
                if depth == 'LOW':
                    a_queries: list[str] = a_queries[:3]
                if depth == 'MEDIUM':
                    a_queries: list[str] = a_queries[:5]
                if depth == 'HIGH':
                    a_queries: list[str] = a_queries

                # Add the auxiliary queries to the list
                aux_queries_list.extend(a_queries)

                # Update progress
                self.progress._update_progress(pss.STORMED, f"Stormed {len(a_queries)} extra auxiliary queries for the task '{task}'", {
                    'auxiliary_queries': a_queries
                })

                show_debug(f"Stormed {len(a_queries)} extra auxiliary queries for the task '{task}'")

                # Search with auxiliary queries
                results = ts.search_d(m_query, a_queries, max_results_for_each = 10, max_content_length = max_content_length)
                src.append(results)

            # Create knowledge base
            kb: _KnowledgeBaseSet = src.to_rag(self.rag, False)

            # Match the queries with the knowledge base
            matches = []
            for a_query in a_queries:
                matches.extend(self.rag.match_knowledge(kb, f"{m_query}+{a_query}", top_k = 8, threshold_score = 0.8))

            # Update progress
            self.progress._update_progress(pss.TASK_CONCLUDING, f"Concluding the summaries and matches for the task '{task}'", {
                'task': task,
                'summaries': src.get_summaries(),
                'matches': matches,
            })

            show_debug(f"Concluding the summaries and matches for the task '{task}'")

            # Generate task conclusion
            task_conclusion = self.smr.summarize(prompt, "\n".join(src.get_summaries() + [match[1] for match in matches]))

            # Append the conclusion to the task conclusions list
            task_conclusions.append(task_conclusion)

            # Update progress
            self.progress._update_progress(pss.TASK_CONCLUDED, f"Concluded the summaries and matches for the task '{task}'", {
                'task': task,
                'summaries': src.get_summaries(),
                'matches': matches,
                'task_conclusion': task_conclusion
            })

            show_debug(f"Concluded the summaries and matches for the task '{task}'")

            # Append sources to the sources list
            sources.extend(src.get_sources())

        # Final conclusion
        
        # Update progress
        self.progress._update_progress(pss.FINAL_CONCLUDING, f"Concluding the summaries for the prompt '{prompt}'")

        show_debug(f"Concluding the summaries for the prompt '{prompt}'")

        # Generate final conclusion
        final_conclusion = self.smr.summarize(prompt, "\n".join(task_conclusions), stream_cb)

        # Update progress
        self.progress._update_progress(pss.FINAL_CONCLUDED, f"Concluded the summaries for the prompt '{prompt}'", {
            'prompt': prompt,
            'tasks': tasks,
            'task_conclusions': task_conclusions,
            'conclusion': final_conclusion
        })

        show_debug(f"Concluded the summaries for the prompt '{prompt}'")

        # Update progress
        self.progress._update_progress(pss.COMPLETED, f"Search completed for the prompt '{prompt}'", {
            'prompt': prompt,
            'tasks': tasks,
            'task_conclusions': task_conclusions,
            'conclusion': task_conclusion,
            'sources': sources
        })

        show_debug(f"Search completed for the prompt '{prompt}'")

        self.progress._update_progress(pss.IDLE)

        # Return the conclusion
        return task_conclusion