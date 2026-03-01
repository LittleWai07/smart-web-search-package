"""
SmartWebSearch.AIModel
~~~~~~~~~~~~

This module implements the AIModel for managing the AI model used for the web searching.
"""

# Import the required modules
import os, requests, json
from typing import Any, TypeAlias, Literal, Callable
from SmartWebSearch.KeyCheck import InvalidKeyError

# AIModel Class
class AIModel:
    """
    AIModel class for managing the AI model used for the web searching.
    """
    def __init__(self, openai_comp_api_key: str, model: str = "deepseek-chat", openai_comp_api_base_url: str = "https://api.deepseek.com/chat/completions", **kwargs: dict[str, Any]):
        """
        Initialize the AIModel object.

        Args:
            openai_comp_api_key (str): The OpenAI Compatible API key.
            model (str): The model to use.
            openai_comp_api_base_url (str): The OpenAI Compatible API base URL.
            **kwargs (dict[str, Any]): Additional keyword arguments in the request body.
        """

        self.model: str = model
        self.openai_comp_api_key: str = openai_comp_api_key
        self.openai_comp_api_base_url: str = openai_comp_api_base_url
        self.kwargs: dict[str, Any] = kwargs

        # Check the OpenAI Compatible API key and model
        self.check()

    def change_model(self, openai_comp_api_key: str, model: str = "deepseek-chat", openai_comp_api_base_url: str = "https://api.deepseek.com/chat/completions", **kwargs: dict[str, Any]) -> None:
        """
        Change the model of the AIModel object.

        Args:
            openai_comp_api_key (str): The OpenAI Compatible API key.
            model (str): The model to use.
            openai_comp_api_base_url (str): The OpenAI Compatible API base URL.
        """

        # Change the API keys
        self.openai_comp_api_key: str = openai_comp_api_key
        self.model: str = model
        self.openai_comp_api_base_url: str = openai_comp_api_base_url
        self.kwargs: dict[str, Any] = kwargs

        # Check the OpenAI Compatible API key and model
        self.check()

    def check(self, raise_error: bool = True):
        """
        Check the OpenAI Compatible API key and model.

        Args:
            raise_error (bool): Whether to raise an exception if the key is invalid.
        
        Returns:
            bool: True if the OpenAI Compatible API key and model are valid, False otherwise.
        """

        # Send a request to the OpenAI Compatible API to check if the key is valid
        res: requests.Response = requests.post(
            self.openai_comp_api_base_url,
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_comp_api_key}"
            },
            json = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello!"}],
                **self.kwargs
            }
        )

        # If the key is invalid, raise an exception
        if res.status_code != 200 and raise_error:
            raise InvalidKeyError(f"Invalid OpenAI Compatible API key: {self.openai_comp_api_key}")

        return res.status_code == 200
    
    def send_request(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Send a request to the OpenAI Compatible API.

        Args:
            messages (list[dict[str, Any]]): The messages to send.

        Returns:
            dict[str, Any]: The response from the OpenAI Compatible API.
        """

        # Send a request to the OpenAI Compatible API
        res: requests.Response = requests.post(
            self.openai_comp_api_base_url,
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_comp_api_key}"
            },
            json = {
                "model": self.model,
                "messages": messages,
                **self.kwargs
            }
        )

        # Raise an exception if the request fails
        res.raise_for_status()

        return res.json()
    
    def send_request_stream(self, messages: list[dict[str, Any]], stream_cb: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
        """
        Send a request to the OpenAI Compatible API in stream mode.

        Args:
            messages (list[dict[str, Any]]): The messages to send.
            stream_cb (Callable[[dict[str, Any]], None]): The callback function for stream.

        Returns:
            dict[str, Any]: The response from the OpenAI Compatible API.
        """

        # Send a request to the OpenAI Compatible API in stream mode
        res: requests.Response = requests.post(
            self.openai_comp_api_base_url,
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_comp_api_key}"
            },
            json = {
                "stream": True,
                "model": self.model,
                "messages": messages,
                **self.kwargs
            },
            stream = True
        )

        # Raise an exception if the request fails
        res.raise_for_status()

        # Loop through the response iterator
        content: str = ''
        created: int = 0
        system_fingerprint: str = ''
        usage: dict[str, Any] = {}

        for chunk in res.iter_lines():
            if not chunk:
                continue

            # Parse each chunk to a dictionary data
            chunk: str = chunk.decode("utf-8").replace("data:", "").strip()

            if chunk == "[DONE]":
                break

            stream_cb(json.loads(chunk))

            # Append the chunk to the content
            content += json.loads(chunk)["choices"][0]["delta"]["content"] if json.loads(chunk)["choices"][0]["delta"].get("content") else ''

            # Update the usage
            if "usage" in json.loads(chunk):
                usage: dict[str, Any] = json.loads(chunk)["usage"]

            # Update the created
            if "created" in json.loads(chunk):
                created: int = json.loads(chunk)["created"]

            # Update the system fingerprint
            if "system_fingerprint" in json.loads(chunk):
                system_fingerprint: str = json.loads(chunk)["system_fingerprint"]

        # Return the response
        return {
            'created': created,
            'object': 'chat.completion',
            'model': self.model,
            'system_fingerprint': system_fingerprint,
            'choices': [
                {
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': content
                    },
                    'logprobs': None,
                    'finish_reason': 'stop'
                }
            ],
            'usage': usage
        }