"""
SmartWebSearch.TavilySearch
~~~~~~~~~~~~

This module implements the TavilySearch API.
"""

# Import the required modules
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, PageElement
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json, os, sys, shutil, re
from markdownify import markdownify
from tavily import TavilyClient
from typing import Any
from SmartWebSearch.Debugger import show_debug, create_debug_file

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
    def __init__(self, id: int, title: str, url: str, snippet: str, score: float, page_content: _PageContent):
        """
        Initialize the _SearchResult object.

        Args:
            id (int): The ID of the search result.
            title (str): The title of the search result.
            url (str): The URL of the search result.
            snippet (str): The snippet of the search result.
            score (float): The score of the search result.
            page_content (_PageContent): The page content of the search result.

        Returns:
            None
        """

        self.id: int = id
        self.title: str = title
        self.url: str = url
        self.snippet: str = snippet
        self.score: float = score
        self.page_content: _PageContent = page_content

    def __str__(self) -> str:
        """
        Return the title of the search result.

        Returns:
            str: The title of the search result.
        """

        return f"_SearchResult(id={self.id}, title='{self.title}', url='{self.url}', snippet='{self.snippet[:50].replace('\n', '\\n')}...', score={self.score}, page_content=_PageContent(content='{self.page_content.content[:50].replace('\n', '\\n')}...', ...))"
    
    def __repr__(self) -> str:
        """
        Return the string representation of the _SearchResult object.

        Returns:
            str: The string representation of the _SearchResult object.
        """

        return f"_SearchResult(id={self.id}, title='{self.title}', url='{self.url}', snippet='{self.snippet[:50].replace('\n', '\\n')}...', score={self.score}, page_content=_PageContent(content='{self.page_content.content[:50].replace('\n', '\\n')}...', ...))"

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
        self.results_count: int = len(results)
        self.results: list[_SearchResult] = results

    def __str__(self) -> str:
        """
        Return the summary of the search results.

        Returns:
            str: The summary of the search results.
        """

        return f"_SearchResults(query='{self.query}', summary='{self.summary[:50]}...', results_count={self.results_count}, results=[{', '.join([f'_SearchResult(title={result.title}, ...)' for result in self.results])}])"
    
    def __repr__(self) -> str:
        """
        Return the string representation of the _SearchResults object.

        Returns:
            str: The string representation of the _SearchResults object.
        """

        return f"_SearchResults(query='{self.query}', summary='{self.summary[:50]}...', results_count={self.results_count}, results=[{', '.join([f'_SearchResult(title={result.title}, ...)' for result in self.results])}])"

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

        # Set the API key
        self.api_key: str = api_key

    def __search(self, query: str, max_results: int = 10) -> _SearchResults:
        """
        Search for a query using Tavily API.

        Args:
            query (str): The search query.
            max_results (int) = 10: The maximum number of results to return.

        Returns:
            _SearchResults: The search results.
        """

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
            "sap.com",
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

        show_debug(f"{len(results['results'])} results found for query: {query}, summary for the results: {results['answer']}")            

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
                    )
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

        # Create a headless Chrome browser
        chrome_options: Options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")

        driver: Chrome = Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)

        show_debug(f"Created Chrome browser, loading URL {idx}/{total_results}: {url}")

        # Load the URL
        try:
            driver.get(url)
        except Exception:
            print("[ERROR] Request timed out, returning empty content.")
            return _PageContent(
                url = url,
                content = None
            )

        show_debug(f"Loaded URL {idx}/{total_results}: {url}")

        # Get the page source
        page_source: str = driver.page_source

        # Close the browser
        driver.quit()

        show_debug(f"Closed Chrome browser, parsing content from URL {idx}/{total_results}: {url}")

        # Parse the page source with BeautifulSoup
        soup: BeautifulSoup = BeautifulSoup(page_source, "html.parser")

        # Parse the content
        parsed_html: str = ""

        # Remove all unnecessary tags
        unnecessary_tags: list[str] = ["script", "style", "link", "meta", "nav", "header", "footer", "aside", "img", "button", "form", "input", "svg", "canvas", "figure", "select"]
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
            "footer"
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

        # If the parsed markdown length less than 5000 characters, empty it directly, and see it as no content
        if len(parsed_markdown) < 5000:
            parsed_markdown: str = ""

        show_debug(f"Parsed content from URL {idx}/{total_results}: {url}")

        create_debug_file(
            filename = f"parsed-content-{idx}",
            ext = "md",
            content = f"URL: {url}\n\n{parsed_markdown}"
        )

        # Return the parsed content
        return _PageContent(
            url = url,
            content = parsed_markdown
        )

    def search(self, query: str) -> _SearchResults:
        """
        Search for a query using Tavily API.

        Args:
            query (str): The search query.

        Returns:
            _SearchResults: The search results.
        """

        show_debug(f"Searching for query: {query}")

        results: _SearchResults = self.__search(query, 15)

        # Return the search results
        return results

    def search_d(self, query: str, extra_details: list[str] = []) -> list[_SearchResults]:
        """
        Search for a query using Tavily API with extra details.

        Args:
            query (str): The search query.
            extra_details (list[str]) = []: The list of extra details to include in the page content of the search results.

        Returns:
            list[_SearchResults]: The search results.
        """

        # Check if extra details are provided
        if len(extra_details) == 0:
            raise InvalidParameterError("An empty list of extra details provided.")

        # Search for a query using Tavily API
        results: list[_SearchResults] = []
        for detail in extra_details:
            current_query: str = f"{query.strip().replace(' ', '+')}+{detail.strip().replace(' ', '+')}"

            show_debug(f"Searching for query: {current_query}")

            results.append(self.__search(current_query))

        # Return the search results
        return results