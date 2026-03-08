# SmartWebSearch Package Documentation

---

## TavilySearch

### Table of Contents

- [Introduction](#introduction)
- [Classes](#classes)
- [TavilySearch](#tavilysearch)
- [_PageContent](#_pagecontent)
- [_SearchResults](#_searchresults)
- [_SearchResult](#_searchresult)
- [SearchResultsContainer](#searchresultscontainer)
- [InvalidParameterError](#invalidparameterror)
- [License](#license)

---

### Introduction

- The TavilySearch module provides the ways to interact with Tavily API to fetch relevant search results.

---

### Classes

There are these classes in the TavilySearch module:

- `TavilySearch`: This class provides the ways to interact with Tavily API to fetch relevant search results.
- `_PageContent`: This class represents the page content.
- `_SearchResults`: This class represents the search results.
- `_SearchResult`: This class represents a single search result.
- `SearchResultsContainer`: This class provides a container for storing search results.
- `InvalidParameterError`: This exception is raised when any invalid parameter is provided to the `TavilySearch` class.

---

#### TavilySearch

- The `TavilySearch` class provides the ways to interact with Tavily API to fetch relevant search results.

##### \_\_init\_\_

- The `__init__` method is the constructor of the `TavilySearch` class.

```python
def __init__(self, api_key: str) -> None:
    """
        Initialize the TavilySearch object.

        Args:
            api_key (str): The Tavily API key.

        Returns:
            None
    """
    ...
```

##### __search

- The `__search` method is used to search for a query using Tavily API.
- This method will call `__parse` methods in threads to fetch and filter the page content after searching if `include_page_content` is set to `True`.
- This method is private and should not be called directly.

```python
def __search(self, query: str, max_results: int = 10, include_page_content: bool = True, max_content_length: int = 150000) -> _SearchResults:
        """
        Search for a query using Tavily API.

        Args:
            query (str): The search query.
            max_results (int) = 10: The maximum number of results to return.
            include_page_content (bool) = True: Whether to include page content.
            max_content_length (int) = 150000: The maximum length of the page content fetched.

        Returns:
            _SearchResults: The search results.
        """
        ...
```

##### __filter

- The `__filter` method is used to filter search results.
- This method is private and should not be called directly.

```python
def __filter(self, html_source: str, url: str) -> str:
    """
    Parse and filter the page content.

    Args:
        html_source (str): The page source.
        url (str): The url of the page.

    Returns:
        str: The filtered page content.
    """
    ...
```

##### __fetch

- The `__fetch` method is used to fetch the page source.
- This method is private and should not be called directly.

```python
def __fetch(self, url: str) -> str:
    """
    Fetch the page source.

    Args:
        url (str): The url of the page.

    Returns:
        str: The page source.
    """
    ...
```

##### __parse

- The `__parse` method is used to parse the page source, extract the page content, and store it in the page_content attribute of each search result.
- This method will call `__fetch` and `__filter` methods to fetch and filter the page content.
- This method will be called in threads to speed up the parsing process.
- This method is private and should not be called directly.

```python
def __parse(self, query: str, search_result: _SearchResult, search_results: list[_SearchResult], total_results: int = 0, max_content_length: int = 150000) -> None:
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
    ...
```

##### search

- The `search` method is used to search for a query using Tavily API.
- This method will call `__search` method to search for a query using Tavily API.

```python
def search(self, query: str, max_results: int = 10, include_page_content: bool = True, max_content_length: int = 150000) -> _SearchResults:
    """
    Search for a query using Tavily API.

    Args:
        query (str): The search query.
        max_results (int) = 10: The maximum number of results to return.
        include_page_content (bool) = True: Whether to include page content.
        max_content_length (int) = 150000: The maximum length of the page content fetched.

    Returns:
        _SearchResults: The search results.
    """
    ...
```

##### search_d

- The `search_d` method is used to search for a query and auxiliary queries using Tavily API.
- This method will call `__search` method to search for queries using Tavily API.

```python
def search_d(self, query: str, aux_queries: list[str] = [], include_page_content: bool = True, include_main_query: bool = False, max_results_for_each: int = 6, max_content_length: int = 150000) -> list[_SearchResults]:
    """
    Search for a query using Tavily API with auxiliary queries.

    Args:
        query (str): The search query.
        aux_queries (list[str]) = []: The list of auxiliary queries that will be added to the search query and searched separately.
        include_page_content (bool) = True: Whether to include page content.
        include_main_query (bool) = False: Whether to include the main query in the page content of the search results.
        max_results_for_each (int) = 6: The maximum number of results to return for each query (including the main query and the auxiliary queries).
        max_content_length (int) = 150000: The maximum length of the page content fetched.

    Returns:
        list[_SearchResults]: The search results.
    """
    ...
```

---

#### _PageContent

- The `_PageContent` class is used to store the page content of a search result.

##### \_\_init\_\_

- The `__init__` method is the constructor of the `_PageContent` class.

```python
def __init__(self, url: str, content: str):
    """
    Initialize the _PageContent object.

    Args:
        url (str): The URL of the page.
        content (str): The content of the page.

    Returns:
        None
    """
    ...
```

##### \_\_str\_\_

- The `__str__` method is used to return the string representation of the `_PageContent` object.

```python
def __str__(self) -> str:
    """
    Return the string representation of the _PageContent object.

    Returns:
        str: The string representation of the _PageContent object.
    """
    ...
```

##### \_\_repr\_\_

- The `__repr__` method is used to return the string representation of the `_PageContent` object.
- This method will call `__str__` method to return the string representation of the `_PageContent` object.

```python
def __repr__(self) -> str:
    """
    Return the string representation of the _PageContent object.

    Returns:
        str: The string representation of the _PageContent object.
    """
    ...
```

---

#### _SearchResult

- The `_SearchResult` class is used to store the search result.

##### \_\_init\_\_

- The `__init__` method is the constructor of the `_SearchResult` class.

```python
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
    ...
```

##### \_\_str\_\_

- The `__str__` method is used to return the string representation of the `_SearchResult` object.

```python
def __str__(self) -> str:
    """
    Return the string representation of the _SearchResult object.

    Returns:
        str: The string representation of the _SearchResult object.
    """
    ...
```

##### \_\_repr\_\_

- The `__repr__` method is used to return the string representation of the `_SearchResult` object.
- This method will call `__str__` method to return the string representation of the `_SearchResult` object.

```python
def __repr__(self) -> str:
    """
    Return the string representation of the _SearchResult object.

    Returns:
        str: The string representation of the _SearchResult object.
    """
    ...
```

##### to_str

- The `to_str` method is used to return the title, snippet and page content of the `_SearchResult` object.

```python
def to_str(self) -> str:
    """
    Return the title, snippet and page content of the search result.

    Returns:
        str: The title, snippet and page content of the search result.
    """
    ...
```

---

#### _SearchResults

- The `_SearchResults` class is used to store the search results.

##### \_\_init\_\_

- The `__init__` method is the constructor of the `_SearchResults` class.

```python
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
    ...
```

##### \_\_str\_\_

- The `__str__` method is used to return the string representation of the `_SearchResults` object.

```python
def __str__(self) -> str:
    """
    Return the string representation of the _SearchResults object.

    Returns:
        str: The string representation of the _SearchResults object.
    """
    ...
```

##### \_\_repr\_\_

- The `__repr__` method is used to return the string representation of the `_SearchResults` object.

```python
def __repr__(self) -> str:
    """
    Return the string representation of the _SearchResults object.

    Returns:
        str: The string representation of the _SearchResults object.
    """
    ...
```

##### \_\_len\_\_

- The `__len__` method is used to return the number of search results.

```python
def __len__(self) -> int:
    """
    Return the number of the search results.

    Returns:
        int: The number of the search results.
    """
    ...
```

##### \_\_getitem\_\_

- The `__getitem__` method is used to return the search result at the given index.

```python
def __getitem__(self, index: int) -> _SearchResult:
    """
    Return the search result at the given index.

    Args:
        index (int): The index of the search result.

    Returns:
        _SearchResult: The search result at the given index.
    """
    ...
```

##### to_str

- The `to_str` method is used to return the summary and each result of the search results.

```python
def to_str(self, include_summary: bool = True) -> str:
    """
    Return the summary and each result of the search results.

    Args:
        include_summary (bool) = True: Whether to include the summary. Defaults to True.

    Returns:
        str: The summary and each result of the search results.
    """
    ...
```

---

#### SearchResultsContainer

- The `SearchResultsContainer` class is used to centralize and store the search results.

##### \_\_init\_\_

- The `__init__` method is the constructor of the `SearchResultsContainer` class.

```python
def __init__(self):
    """
    Initialize the SearchResultsContainer object.

    Returns:
        None
    """
    ...
```

##### append

- The `append` method is used to append search results to the container.

```python
def append(self, results: _SearchResult | _SearchResults | list[_SearchResult] | list[_SearchResults]) -> None:
    """
    Append search results to the container.

    Args:
        results (_SearchResult | _SearchResults | list[_SearchResult] | list[_SearchResults]): The search results to append.

    Returns:
        None
    """
    ...
```

##### get_summaries

- The `get_summaries` method is used to get the summaries of the search results.

```python
def get_summaries(self) -> list[str]:
    """
    Get the summaries of the search results.

    Returns:
        list[str]: The summaries of the search results.
    """
    ...
```

##### to_str

- The `to_str` method is used to return the summary and each result of the search results.

```python
def to_str(self, include_summary: bool = True) -> str:
    """
    Return the summary and each result of the search results.

    Args:
        include_summary (bool) = True: Whether to include the summary. Defaults to True.

    Returns:
        str: The summary and each result of the search results.
    """
    ...
```

##### to_rag

- The `to_rag` method is used to return the RAGTool object and the knowledge base set.

```python
def to_rag(self, rag_tool: "RAGTool", include_summary: bool = True) -> _KnowledgeBaseSet:
    """
    Return the RAGTool object and the knowledge base set.

    Args:
        rag_tool (RAGTool): The RAGTool object.
        include_summary (bool) = True: Whether to include the summary. Defaults to True.

    Returns:
        _KnowledgeBaseSet: The knowledge base set.
    """
    ...
```

##### to_txt

- The `to_txt` method is used to save the search results to a text file.

```python
def to_txt(self, file_path: str) -> None:
    """
    Save the search results to a text file.

    Args:
        file_path (str): The file path to save the search results.

    Returns:
        None
    """
    ...
```

##### __list

- The `__list` method is used to return the list of search results.
- This method is private and should not be called directly.

```python
def __list(self) -> list[_SearchResult]:
    """
    Return the list of search results.

    Returns:
        list[_SearchResult]: The list of search results.
    """
    ...
```

##### \_\_str\_\_

- The `__str__` method is used to return the string representation of the `SearchResultsContainer` object.

```python
def __str__(self) -> str:
    """
    Return the string representation of the SearchResultsContainer object.

    Returns:
        str: The string representation of the SearchResultsContainer object.
    """
    ...
```

##### \_\_repr\_\_

- The `__repr__` method is used to return the string representation of the `SearchResultsContainer` object.

```python
def __repr__(self) -> str:
    """
    Return the string representation of the SearchResultsContainer object.

    Returns:
        str: The string representation of the SearchResultsContainer object.
    """
    ...
```

##### \_\_len\_\_

- The `__len__` method is used to return the number of search results.

```python
def __len__(self) -> int:
    """
    Return the number of search results.

    Returns:
        int: The number of search results.
    """
    ...
```

##### \_\_getitem\_\_

- The `__getitem__` method is used to return the search result at the given index.

```python
def __getitem__(self, index: int) -> _SearchResult:
    """
    Return the search result at the given index.

    Args:
        index (int): The index of the search result.

    Returns:
        _SearchResult: The search result at the given index.
    """
    ...
```

---

#### InvalidParameterError

- The `InvalidParameterError` exception is raised when any invalid parameter is provided to the `TavilySearch` class.
- This class inherits from the `Exception` class.

##### \_\_init\_\_

- The `__init__` method is the constructor of the `InvalidParameterError` exception.

```python
def __init__(self, message: str) -> None:
    """
    Initialize the InvalidParameterError exception.

    Args:    
        message (str): The error message.

    Returns:
        None
    """    
    ...
```

---

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/LittleWai07/smart-web-search-package/blob/main/LICENSE) file for details