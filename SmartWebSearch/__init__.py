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
from SmartWebSearch.Progress import Progress, _ProgressData, ProgressStatusSelector
from SmartWebSearch.SmartWebSearch import SmartWebSearch
from typing import Callable, Any

# Set the debugging mode
DebuggerConfiguration.DEBUGGING = True
DebuggerConfiguration.CREATE_DEBUG_FILES = False
DebuggerConfiguration.SKIP_LOW_IMPORTANCE = True

# Print the version of the package
__version__ = "1.3.2"

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