"""
SmartWebSearch.TavilySearch
~~~~~~~~~~~~

This module implements the TavilySearch API.
"""

# Import the required modules
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, PageElement
from markdownify import markdownify
from tavily import TavilyClient
from typing import Any, TYPE_CHECKING
from SmartWebSearch.Debugger import show_debug, create_debug_file
from SmartWebSearch.ChromeDriver import ChromeDriver
from SmartWebSearch.KeyCheck import KeyCheck
from threading import Thread, active_count
from SmartWebSearch.Progress import Progress
from SmartWebSearch.Progress import ProgressStatusSelector as pss
import time

if TYPE_CHECKING:
    from SmartWebSearch.RAGTool import RAGTool, _KnowledgeBaseSet

class _PageContent:
    """
    A class for managing page content.
    """
    def __init__(self, url: str, content: str):
        """
        Initialize the _PageContent object.

        Args:
            url (str): The URL of the page.
            content (str): The content of the page.

        Returns:
            None
        """

        self.url: str = url
        self.content: str = content

    def __str__(self) -> str:
        """
        Return the content of the page.

        Returns:
            str: The content of the page.
        """

        return f"_PageContent(url='{self.url}', content='{self.content[:50].replace('\n', '\\n')}...')"
    
    def __repr__(self) -> str:
        """
        Return the string representation of the _PageContent object.

        Returns:
            str: The string representation of the _PageContent object.
        """

        return f"_PageContent(url='{self.url}', content='{self.content[:50].replace('\n', '\\n')}...')"

class _SearchResult:
    """
    A class for managing search result.
    """
    def __init__(self, id: int, title: str, url: str, snippet: str, score: float, page_content: _PageContent | None = None):
        """
        Initialize the _SearchResult object.

        Args:
            id (int): The ID of the search result.
            title (str): The title of the search result.
            url (str): The URL of the search result.
            snippet (str): The snippet of the search result.
            score (float): The score of the search result.
            page_content (_PageContent | None) = None: The page content of the search result.

        Returns:
            None
        """

        self.id: int = id
        self.title: str = title
        self.url: str = url
        self.snippet: str = snippet
        self.score: float = score
        self.page_content: _PageContent | None = page_content

    def __str__(self) -> str:
        """
        Return the title of the search result.

        Returns:
            str: The title of the search result.
        """

        return f"_SearchResult(id={self.id}, title='{self.title}', url='{self.url}', snippet='{self.snippet[:50].replace('\n', '\\n')}...', score={self.score}, page_content={f"_PageContent(content='{self.page_content.content[:50].replace('\n', '\\n')}...', ...)" if self.page_content else None})"
    
    def __repr__(self) -> str:
        """
        Return the string representation of the _SearchResult object.

        Returns:
            str: The string representation of the _SearchResult object.
        """

        return self.__str__()

    def to_str(self) -> str:
        """
        Return the title, and snippet of the page content.

        Returns:
            str: The title, and snippet of the page content.
        """

        return f"{self.title}\n{self.snippet}" + (f"\n{self.page_content.content}" if self.page_content else "")

class _SearchResults:
    """
    A class for managing search results.
    """
    def __init__(self, query: str, summary: str, results: list[_SearchResult]):
        """
        Initialize the _SearchResults object.

        Args:
            query (str): The search query.
            summary (str): The summary of the search results.
            results (list[_SearchResult]): The list of search results.

        Returns:
            None
        """

        self.query: str = query
        self.summary: str = summary
        self.results: list[_SearchResult] = results

    def __str__(self) -> str:
        """
        Return the summary of the search results.

        Returns:
            str: The summary of the search results.
        """

        return f"_SearchResults(query='{self.query}', summary='{self.summary[:50]}...', results=[{', '.join([f'_SearchResult(title={result.title}, ...)' for result in self.results])}])"
    
    def __repr__(self) -> str:
        """
        Return the string representation of the _SearchResults object.

        Returns:
            str: The string representation of the _SearchResults object.
        """

        return self.__str__()
    
    def __len__(self) -> int:
        """
        Return the length of the search results.

        Returns:
            int: The length of the search results.
        """

        return len(self.results)
    
    def __getitem__(self, index: int) -> _SearchResult:
        """
        Return the search result at the given index.

        Args:
            index (int): The index of the search result.

        Returns:
            _SearchResult: The search result at the given index.
        """

        return self.results[index]

    def to_str(self, include_summary: bool = True) -> str:
        """
        Return the summary and each result of the search results.

        Args:
            include_summary (bool) = True: Whether to include the summary. Defaults to True.

        Returns:
            str: The summary and each result of the search results.
        """

        return (f"{self.summary}\n" if include_summary else "") + "\n".join([result.to_str() for result in self.results])

class SearchResultsContainer:
    """
    A class for centralizing search results.
    """

    def __init__(self):
        """
        Initialize the SearchResultsContainer object.

        Returns:
            None
        """

        self.results: list[_SearchResult | _SearchResults] = []

    def append(self, results: _SearchResult | _SearchResults | list[_SearchResult] | list[_SearchResults]) -> None:
        """
        Append search results to the container.

        Args:
            results (_SearchResult | _SearchResults | list[_SearchResult] | list[_SearchResults]): The search results to append.

        Returns:
            None
        """

        # Check if results is a list
        if isinstance(results, list):
            for result in results:
                # Check if result is a _SearchResult or _SearchResults
                if isinstance(result, _SearchResult):
                    # Check if result is a _SearchResult
                    self.results.append(result)

                elif isinstance(result, _SearchResults):
                    # Check if result is a _SearchResults
                    self.results.append(result)

                else:
                    # Otherwise, raise a TypeError
                    raise TypeError(f"Expected _SearchResult or _SearchResults, got {type(result)}")
        
        elif isinstance(results, _SearchResult):
            # Check if results is a _SearchResult
            self.results.append(results)

        elif isinstance(results, _SearchResults):
            # Check if results is a _SearchResults
            self.results.append(results)

        else:
            # Otherwise, raise a TypeError
            raise TypeError(f"Expected _SearchResult or _SearchResults, got {type(results)}")
        
    def get_summaries(self) -> list[str]:
        """
        Return the summaries of the search results.

        Returns:
            list[str]: The summaries of the search results.
        """

        return [result.summary for result in self.results if isinstance(result, _SearchResults)]
        
    def __list(self):
        """
        Return the list of search results.

        Returns:
            list[_SearchResult]: The list of search results.
        """

        results: list[_SearchResult] = []

        for result in self.results:
            if isinstance(result, _SearchResults):
                for result in result.results:
                    # Check if result url repeated
                    if result.url in [r.url for r in results]:
                        continue
                    results.append(result)
            else:
                # Check if result url repeated
                if result.url in [r.url for r in results]:
                    continue
                results.append(result)

        return results
        
    def __str__(self):
        """
        Return the summary and each result of the search results.

        Returns:
            str: The summary and each result of the search results.
        """

        return f"SearchResultsContainer(results=[{', '.join([f'_SearchResult(title={result.title[:50]}, ...)' for result in self.__list()])}])"
    
    def __repr__(self):
        """
        Return the string representation of the SearchResultsContainer object.

        Returns:
            str: The string representation of the SearchResultsContainer object.
        """

        return self.__str__()
    
    def __len__(self):
        """
        Return the length of the search results.

        Returns:
            int: The length of the search results.
        """

        length: int = 0

        for result in self.results:
            if isinstance(result, _SearchResults):
                length += len(result)
            else:
                length += 1

        return length
    
    def __getitem__(self, index):
        """
        Return the search result at the given index.

        Args:
            index (int): The index of the search result.

        Returns:
            _SearchResult: The search result at the given index.
        """

        return self.__list()[index]
        
    def to_str(self, include_summary: bool = True) -> str:
        """
        Return the summary and each result of the search results.

        Args:
            include_summary (bool) = True: Whether to include the summary. Defaults to True.

        Returns:
            str: The summary and each result of the search results.
        """

        return "\n".join([result.to_str(include_summary = include_summary) if isinstance(result, _SearchResults) else result.to_str() for result in self.results])
    
    def to_rag(self, rag_tool: "RAGTool", include_summary: bool = True) -> "_KnowledgeBaseSet":
        """
        Return the RAGTool object.

        Args:
            rag_tool (RAGTool): The RAGTool object.
            include_summary (bool) = True: Whether to include the summary. Defaults to True.

        Returns:
            _KnowledgeBaseSet: The knowledge base set.
        """

        # Build the knowledge base
        kl_base_set: _KnowledgeBaseSet = rag_tool.build_knowledge(self.to_str(include_summary = include_summary))

        # Return the RAGTool object and the knowledge base set
        return kl_base_set
    
    def to_txt(self, file_path: str = "search_results.txt") -> None:
        """
        Save the search results to a text file.

        Args:
            file_path (str) = "search_results.txt": The file path to save the search results.

        Returns:
            None
        """

        # Save the search results to a text file
        with open(file_path, "w", encoding = "utf-8") as f:
            f.write(self.to_str())

class InvalidParameterError(Exception):
    """
    An exception raised when an invalid parameter is provided.
    """
    def __init__(self, message: str) -> None:
        """
        Initialize the InvalidParameterError object.

        Args:
            message (str): The error message.

        Returns:
            None
        """

        self.message: str = message
        super().__init__(self.message)

class InactiveError(Exception):
    """
    An exception raised when the TavilySearch object is inactive.
    """
    def __init__(self, message: str) -> None:
        """
        Initialize the InactiveError object.

        Args:
            message (str): The error message.

        Returns:
            None
        """

        self.message: str = message
        super().__init__(self.message)

# The TavilySearch class
class TavilySearch:
    """
    A class for web searching with Tavily API.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the TavilySearch object.

        Args:
            api_key (str): The Tavily API key.

        Returns:
            None
        """

        # Check the API key
        KeyCheck.check_tavily_api_key(api_key)
        
        # Initialize the TavilyClient object
        self.client: TavilyClient = TavilyClient(api_key)

        # Initialize the Progress object
        self.progress: Progress = Progress()

        # Set the API key
        self.api_key: str = api_key

    def __search(self, query: str, max_results: int = 10, include_page_content: bool = True) -> _SearchResults:
        """
        Search for a query using Tavily API.

        Args:
            query (str): The search query.
            max_results (int) = 10: The maximum number of results to return.
            include_page_content (bool) = True: Whether to include page content.

        Returns:
            _SearchResults: The search results.
        """

        # Update progress
        self.progress._update_progress(pss.SEARCHING, f"Searching for '{query}'")

        # Search for a query using Tavily API
        results: dict[str, Any] = dict(
            self.client.search(
                query = query.replace(' ', '+'),
                max_results = max_results,
                include_answer = "advanced"
            )
        )

        # Filtered out results that url is invalid
        invalid_sites: list[str] = [
            "apps",
            "play",
            "maps",
            "drive",
            "mail",
            "calendar",
            ".vip",
            ".top",
            ".club",
            ".xyz",
            ".wang",
            ".cc",
            ".info",
            ".tool",
            ".download",
            ".apk",
            ".zip",
            ".exe",
            ".pdf",
            "weibo.com",
            "douyin.com",
            "bilibili.com",
            "tiktok.com",
            "youtube.com",
            "hao123.com",
            "2345.com",
            "instagram.com",
            "cloudflare.com",
            "stackoverflow.com",
            "soundcloud.com",
            "sap.com",
            "ebay.com",
            "ad.",
            "nav.",
            "tool.",
            "/login",
            "/register",
            "/download",
            "/upload",
            "/pay",
            "/cart",
            "/about",
            "/contact",
            "/help",
            "/faq",
            "/menu",
            "/nav",
            "/widget",
            "/ad/",
            "/sponsor",
            "/promo",
            "?from=",
            "?adid=",
            "?track=",
            "shorturl.at",
            "url.cn",
            "t.cn",
            "bit.ly"
        ]

        tmp_results: list[dict[str, Any]] = results["results"]
        results["results"] = []
        for result in tmp_results:
            for invalid_site in invalid_sites:
                if invalid_site in result["url"]:
                    break
            else:
                results["results"].append(result)

        show_debug(f"{len(results['results'])} results found for query: {query}")
        show_debug(f"Summary for the results: {results['answer']}", importance = "LOW")

        # Create a list to store search results
        search_results: list[_SearchResult] = [
            _SearchResult(
                id = idx, # The id of the result
                title = result["title"], # The title of the page
                url = result["url"], # The url of the page
                snippet = result["content"], # The snippet of the page
                score = round(result["score"] * 100, 2), # The score of the result
                page_content = _PageContent(
                    url = result["url"], # The url of the page
                    content = "" # The content of the page (an empty string now, it will be added later)
                ) if include_page_content else None
            )
            for idx, result in enumerate(results["results"], start = 1)
        ]

        # Update progress
        self.progress._update_progress(pss.SEARCHED, f"Found {len(results['results'])} results for query: '{query}'", {
            "query": query,
            "summary": results["answer"],
            "results": search_results,
            "total_results": len(results["results"])
        })

        # If page content is not included, return the search results
        if not include_page_content:
            search_results_obj: _SearchResults = _SearchResults(
                query = query, # The search query
                summary = results["answer"] if "answer" in results else "", # The summary of the search results
                results = search_results
            )

            self.progress._update_progress(pss.PART_COMPLETED, f"Completed searching for query: '{query}'", {
                "query": query,
                "summary": results["answer"],
                "results": search_results_obj,
                "total_content_length": None,
                "total_results": len(results["results"])
            })

            return search_results_obj
        
        # If page content is included
        
        # Create a list to store parsed search results
        parsed_search_results: list[_SearchResult] = []

        # Loop through the results
        for search_result in search_results:
            # Parse the page in threads
            # The parse function will fetch the page content, and parse and filter it
            # Then it will add the page content to the _SearchResult object
            # Finally, it will add the _SearchResult object to the parsed_search_results list
            thread: Thread = Thread(target = self.__parse, args = (
                query,
                search_result,
                parsed_search_results,
                len(results["results"])
            ))
            thread.daemon = True

            # Start the thread
            thread.start()

        # Wait until all threads are done
        while len(parsed_search_results) < len(results["results"]):
            pass

        # Calculate the total content length
        total_content_length: int = sum([ len(result.page_content.content) for result in parsed_search_results ])

        show_debug(f"{len(search_results)} results parsed for query: {query}, total content length is {total_content_length} characters")

        # Update progress
        self.progress._update_progress(pss.PARSED, f"Parsed {len(search_results)} results for query: '{query}', total content length is {total_content_length} characters", {
            "query": query,
            "summary": results["answer"],
            "results": parsed_search_results,
            "total_content_length": total_content_length,
            "total_results": len(search_results)
        })

        # Create the _SearchResults object
        search_results_obj: _SearchResults = _SearchResults(
            query = query.replace(' ', '+'), # The query to search
            summary = results["answer"] if results["answer"] else "", # The summary
            results = parsed_search_results
        )

        self.progress._update_progress(pss.PART_COMPLETED, f"Completed searching for query: '{query}'", {
            "query": query,
            "summary": results["answer"],
            "results": search_results_obj,
            "total_results": len(results["results"])
        })

        # Return the results
        return search_results_obj
    
    def __filter(self, html_source: str, url: str) -> str:
        """
        Parse and filter the page content.

        Args:
            html_source (str): The page source.
            url (str): The url of the page.

        Returns:
            str: The filtered page content.
        """

        # Parse the page source with BeautifulSoup
        soup: BeautifulSoup = BeautifulSoup(html_source, "html.parser")

        # Parse the content
        parsed_html: str = ""

        # Remove all unnecessary tags
        unnecessary_tags: list[str] = ["script", "style", "link", "meta", "nav", "header", "footer", "aside", "img", "button", "form", "input", "svg", "canvas", "figure", "select", "checkbox", "label"]
        for tag in unnecessary_tags:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove all blank text nodes
        for elem in soup.find_all():
            if elem.text.strip() == "":
                elem.decompose()

        # Remove unnecessary attributes from all tags
        for element in soup.find_all():
            for attr in list(element.attrs):
                if attr not in ["class", "id"]:
                    del element.attrs[attr]

        # Remove tags with invalid ids and classes
        invalid_ids: list[str] = [
            "nav"
        ]
        invalid_classes: list[str] = [
            "navig",
            "navbar",
            "dropdown",
            "clickable",
            "option",
            "select",
            "error",
            "banner",
            "reference",
            "preference",
            "appearance",
            "notice",
            "cookie",
            "awsccc",
            "menu",
            "footer",
            "region-container",
            "region-list"
        ]

        for element in soup.find_all():
            if element.name in ["html", "head", "body"]: continue

            for attr in ["id", "class"]:
                if not (element and element.attrs): continue
                if element.decomposed: continue

                if element.get(attr):
                    for invalid_id in invalid_ids:
                        if invalid_id in element.get(attr):
                            element.decompose()
                            break

        # Get the parsed HTML
        parsed_html: str = str(soup.find("body")) if soup.find("body") else ""

        # Convert to Markdown format
        parsed_markdown: str = markdownify(parsed_html)

        # Remove all unnecessary line breaks and extra spaces
        while "\n\n" in parsed_markdown:
            parsed_markdown = parsed_markdown.replace("\n\n", "\n")
        while "  " in parsed_markdown:
            parsed_markdown = parsed_markdown.replace("  ", " ")

        # If the parsed markdown length less than 550 characters
        if len(parsed_markdown) < 550:
            # If the parsed markdown contains the invalid keywords
            for keyword in ["javascript", "cookie", "human", "enable", "verify", "err", "error"]:
                if keyword in parsed_markdown.lower():

                    show_debug(f"Found invalid keyword '{keyword}' (appeared {parsed_markdown.lower().count(keyword)} times) in parsed content from URL: {url}", importance = "LOW")
                    show_debug(f"Entire parsed content from URL ('{url}'): {parsed_markdown.replace("\n", "\\n")}", importance = "LOW")

                    # Remove the parsed markdown
                    parsed_markdown = ""
                    break

        # If the parsed markdown length less than 400 characters
        if len(parsed_markdown) < 400:
            # Remove the parsed markdown
            parsed_markdown = ""

        # Return the parsed markdown
        return parsed_markdown
    
    def __fetch(self, url: str) -> str:
        """
        Fetch the page source.

        Args:
            url (str): The url of the page.

        Returns:
            str: The page source.
        """

        # Create a chrome driver
        chrome_driver: ChromeDriver = ChromeDriver()

        try:
            # Load the URL
            chrome_driver.driver.get(url)

            # Get the page source
            page_source: str = chrome_driver.driver.page_source

        except Exception:
            # Request timeout
            # Return an empty string
            return ""
        
        finally:
            # Quit the driver
            chrome_driver.quit()

        # Return the page source
        return page_source

    def __parse(self, query: str, search_result: _SearchResult, search_results: list[_SearchResult], total_results: int = 0) -> None:
        """
        Fetch and parse the page source, extract the page content, store it in the page_content attribute of the search result and append it to the list of search results.

        Args:
            query (str): The search query.
            search_result (_SearchResult): The search result.
            search_results (list[_SearchResult]): The list of search results.
            total_results (int): The total number of results.

        Returns:
            None
        """

        # Process the parsing task
        show_debug(f"Processing parsing task for URL: {search_result.url}", importance = "LOW")

        # Fetch the URL in the browser
        show_debug(f"Fetching URL: {search_result.url}", importance = "LOW")

        # Get the page source
        page_source: str = self.__fetch(search_result.url)

        # If the page source is empty
        if not page_source:
            # Append the search result to the search results list
            search_results.append(search_result)

            show_debug(f"Request timed out, returned empty content, URL: {search_result.url}", type = "ERROR")
            show_debug(f"Finished parsing task {len(search_results)}/{total_results}")

            # Update the progress
            self.progress._update_progress(pss.PARSED, f"Request timed out, returned empty content, parsed {len(search_results)}/{total_results} results for query '{query}'", {
                "error": "REQUEST_TIMEOUT",
                "query": query,
                "current": len(search_results),
                "total": total_results,
                "search_result": search_result
            }, len(search_results) / total_results)

            # Return
            return

        show_debug(f"Fetched URL: {search_result.url}", importance = "LOW")

        show_debug(f"Filtering content from URL: {search_result.url}", importance = "LOW")

        # Parse the page source
        parsed_markdown: str = self.__filter(page_source, search_result.url)        

        show_debug(f"Filtered content from URL: {search_result.url}, length: {len(parsed_markdown)}", importance = "LOW")

        create_debug_file(
            filename = f"parsed-content",
            ext = "md",
            content = f"URL: {search_result.url}\n\n{parsed_markdown}"
        )

        # Set the page content to the parsed markdown
        # Get the first 150,000 characters of the parsed markdown only if parsed markdown has more than 150,000 characters
        search_result.page_content.content = parsed_markdown[:150000]
        
        # Append the search result to the search results list
        search_results.append(search_result)

        show_debug(f"Finished parsing task {len(search_results)}/{total_results}")

        # Update the progress
        self.progress._update_progress(pss.PARSING, f"Parsed {len(search_results)}/{total_results} results for query '{query}'", {
            "error": None,
            "query": query,
            "current": len(search_results),
            "total": total_results,
            "search_result": search_result
        }, len(search_results) / total_results)

        # Sleep 0.1 seconds
        time.sleep(0.1)

    def search(self, query: str, include_page_content: bool = True, max_results: int = 10) -> _SearchResults:
        """
        Search for a query using Tavily API.

        Args:
            query (str): The search query.
            include_page_content (bool) = True: Whether to include page content.
            max_results (int) = 10: The maximum number of results to return.

        Returns:
            _SearchResults: The search results.
        """

        show_debug(f"Searching for query: {query.replace(' ', '+')}")

        results: _SearchResults = self.__search(query.replace(' ', '+'), max_results, include_page_content)

        # Update the progress
        self.progress._update_progress(pss.COMPLETED, f"Found {len(results.results)} results for query {query}", {
            "query": query,
            "search_results": results
        })

        self.progress._update_progress(pss.IDLE)

        # Return the search results
        return results

    def search_d(self, query: str, aux_queries: list[str] = [], include_page_content: bool = True, include_main_query: bool = False, max_results_for_each: int = 6) -> list[_SearchResults]:
        """
        Search for a query using Tavily API with auxiliary queries.

        Args:
            query (str): The search query.
            aux_queries (list[str]) = []: The list of auxiliary queries that will be added to the search query and searched separately.
            include_page_content (bool) = True: Whether to include page content.
            include_main_query (bool) = False: Whether to include the main query in the page content of the search results.
            max_results_for_each (int) = 6: The maximum number of results to return for each query (including the main query and the auxiliary queries).

        Returns:
            list[_SearchResults]: The search results.
        """

        # Check if auxiliary queries are provided
        if len(aux_queries) == 0:
            raise InvalidParameterError("An empty list of auxiliary queries provided.")

        # Search for the queries using Tavily API
        results: list[_SearchResults] = []

        # Search for the main query
        if include_main_query:
            show_debug(f"Searching for query: {query.replace(' ', '+')}")

            results.append(self.__search(query.replace(' ', '+'), max_results_for_each, include_page_content))

        # Search for the auxiliary queries with the main query
        for detail in aux_queries:
            current_query: str = f"{query.strip().replace(' ', '+')}+{detail.strip().replace(' ', '+')}"

            show_debug(f"Searching for query: {current_query.replace(' ', '+')}")

            results.append(self.__search(current_query.replace(' ', '+'), max_results_for_each, include_page_content))

        # Update the progress
        self.progress._update_progress(pss.COMPLETED, f"Found {sum([len(search_results.results) for search_results in results])} results for query '{query}' with auxiliary queries {', '.join([f'\'{aux_query}\'' for aux_query in aux_queries])}", {
            "query": query,
            "search_results": results
        })

        self.progress._update_progress(pss.IDLE)

        # Return the search results
        return results