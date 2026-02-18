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
        
        # Initialize the TavilyClient object
        self.client: TavilyClient = TavilyClient(api_key)

        # Initialize the ChromeDriver object
        self.chrome_driver: ChromeDriver = ChromeDriver()

        # Set the status of the TavilySearch object
        self.status: bool = True

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

        # Check the status of the TavilySearch object
        if not self.status: raise InactiveError("TavilySearch object is not active.")

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
        show_debug(f"Summary for the results: {results['results']}", importance = "LOW")

        # Return the results
        return _SearchResults(
            query = query.replace(' ', '+'), # The query to search
            summary = results["answer"], # The summary
            results = [
                _SearchResult(
                    id = idx, # The id of the result
                    title = result["title"], # The title of the page
                    url = result["url"], # The url of the page
                    snippet = result["content"], # The snippet of the page
                    score = round(result["score"] * 100, 2), # The score of the result
                    page_content = self.__parse(
                        url = result["url"], # The url of the page
                        queries = query.replace(' ', '+').split("+"), # The queries to find on the page
                        idx = idx, # The index of the current result
                        total_results = len(results["results"]) # The total number of results
                    ) if include_page_content else None
                )
                for idx, result in enumerate(results["results"], start = 1)
            ]
        )
    
    def __parse(self, url: str, queries: list[str] = [], idx: int = 0, total_results: int = 0) -> _PageContent:
        """
        Parse the content of a URL with HTML source.

        Args:
            url (str): The URL to parse.
            queries (list[str]) = []: The list of queries to search for.
            score (float) = 0: The score of the search result.
            idx (int) = 0: The index of the current result.
            total_results (int) = 0: The total number of results.

        Returns:
            _PageContent: The parsed content.
        """

        # Check the status of the TavilySearch object
        if not self.status: raise InactiveError("TavilySearch object is not active.")

        # Process the parsing task
        show_debug(f"Processing parsing task for URL {idx}/{total_results}: {url}")

        # Load the url in the browser
        show_debug(f"Loading URL {idx}/{total_results}: {url}", importance = "LOW")

        # Load the URL
        try:
            self.chrome_driver.driver.get(url)
        except Exception:
            show_debug("Request timed out, returning empty content.", type = "ERROR")
            return _PageContent(
                url = url,
                content = ""
            )

        show_debug(f"Fetched URL {idx}/{total_results}: {url}", importance = "LOW")

        # Get the page source
        page_source: str = self.chrome_driver.driver.page_source

        show_debug(f"Parsing content from URL {idx}/{total_results}: {url}", importance = "LOW")

        # Parse the page source with BeautifulSoup
        soup: BeautifulSoup = BeautifulSoup(page_source, "html.parser")

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

                    show_debug(f"Found invalid keyword '{keyword}' (appeared {parsed_markdown.lower().count(keyword)} times) in parsed content from URL {idx}/{total_results}: {url}", importance = "LOW")
                    show_debug(f"Entire parsed content from URL {idx}/{total_results}: {parsed_markdown.replace("\n", "\\n")}", importance = "LOW")

                    # Remove the parsed markdown
                    parsed_markdown = ""
                    break

        # If the parsed markdown length less than 400 characters
        if len(parsed_markdown) < 400:
            # Remove the parsed markdown
            parsed_markdown = ""

        show_debug(f"Parsed content from URL {idx}/{total_results}: {url}, length: {len(parsed_markdown)}")

        create_debug_file(
            filename = f"parsed-content",
            ext = "md",
            content = f"URL: {url}\n\n{parsed_markdown}"
        )

        # Return the parsed content
        return _PageContent(
            url = url,
            content = parsed_markdown
        )

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

        # Check the status of the TavilySearch object
        if not self.status: raise InactiveError("TavilySearch object is not active.")

        show_debug(f"Searching for query: {query.replace(' ', '+')}")

        results: _SearchResults = self.__search(query.replace(' ', '+'), max_results, include_page_content)

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

        # Check the status of the TavilySearch object
        if not self.status: raise InactiveError("TavilySearch object is not active.")

        # Check if auxiliary queries are provided
        if len(aux_queries) == 0:
            raise InvalidParameterError("An empty list of auxiliary queries provided.")

        # Search for the queries using Tavily API
        results: list[_SearchResults] = []

        # Search for the main query
        if include_main_query:
            results.append(self.__search(query.replace(' ', '+'), max_results_for_each, include_page_content))

        # Search for the auxiliary queries with the main query
        for detail in aux_queries:
            current_query: str = f"{query.strip().replace(' ', '+')}+{detail.strip().replace(' ', '+')}"

            show_debug(f"Searching for query: {current_query.replace(' ', '+')}")

            results.append(self.__search(current_query.replace(' ', '+'), max_results_for_each, include_page_content))

        # Return the search results
        return results
    
    def quit(self) -> None:
        """
        Quit the TavilySearch object.

        Returns:
            None
        """

        # Check the status of the TavilySearch object
        if not self.status: raise InactiveError("TavilySearch object is not active.")

        # Set the status of the TavilySearch object to False
        self.status = False

        # Quit the ChromeDriver object
        self.chrome_driver.quit()