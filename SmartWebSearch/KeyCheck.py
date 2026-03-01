"""
SmartWebSearch.KeyCheck
~~~~~~~~~~~~

This module implements the KeyCheck Tool for the package.
"""

# Import the required modules
import requests
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SmartWebSearch.AIModel import AIModel

# Exception Class
class InvalidKeyError(Exception):
    """
    An exception for invalid API keys.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the InvalidKeyError object.

        Args:
            message (str): The error message.
        """

        self.message: str = message
        super().__init__(self.message)

# KeyCheck Class
class KeyCheck:
    """
    A class for checking the validity of API keys.
    """

    RAISE_ERROR: bool = True

    # Check if the OpenAI Compatible API key is valid
    @staticmethod
    def check_openai_comp_api_key(ai_model: "AIModel") -> bool:
        """
        Check if the OpenAI Compatible API key is valid.

        Args:
            ai_model (AIModel): The AIModel object.

        Returns:
            bool: True if the key is valid, False otherwise.
        """

        # Return True if the key is valid, False otherwise
        return ai_model.check(KeyCheck.RAISE_ERROR)
    
    # Check if the Tavily API key is valid
    @staticmethod
    def check_tavily_api_key(tavily_api_key: str) -> bool:
        """
        Check if the Tavily API key is valid.

        Args:
            tavily_api_key (str): The Tavily API key.

        Returns:
            bool: True if the key is valid, False otherwise.
        """

        # Send a request to the Tavily API to check if the key is valid
        res: requests.Response = requests.get(
            "https://api.tavily.com/usage",
            headers = {
                "Authorization": f"Bearer {tavily_api_key}"
            }
        )

        # If the key is invalid, raise an exception
        if res.status_code != 200 and KeyCheck.RAISE_ERROR:
            raise InvalidKeyError(f"Invalid Tavily API key: {tavily_api_key}")

        # Return True if the key is valid, False otherwise
        return res.status_code == 200