"""
SmartWebSearch.Summarizer.py
~~~~~~~~~~~~

This module implements the Summarizer Tool for summerizing the search results.
"""

# Import the required modules
import requests, json
from typing import Any, Callable
from SmartWebSearch.KeyCheck import KeyCheck
from datetime import datetime

# Summarizer Class
class Summarizer:
    """
    A class for summarizing the search results.
    """

    @staticmethod
    def __send_request(openai_comp_api_key: str, messages: list[dict[str, Any]], model: str = "deepseek-chat", openai_comp_api_base_url: str = "https://api.deepseek.com/chat/completions") -> dict[str, Any]:
        """
        Send a request to the OpenAI Compatible API.

        Args:
            openai_comp_api_key (str): The OpenAI Compatible API key.
            messages (list[dict[str, Any]]): The messages to send.
            model (str): The model to use.
            openai_comp_api_base_url (str): The OpenAI Compatible API base URL.

        Returns:
            dict[str, Any]: The response from the OpenAI Compatible API.
        """

        # Send a request to the OpenAI Compatible API
        res: requests.Response = requests.post(
            openai_comp_api_base_url,
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_comp_api_key}"
            },
            json = {
                "model": model,
                "messages": messages
            }
        )

        # Raise an exception if the request fails
        res.raise_for_status()

        # Return the response
        return res.json()
    
    def __send_request_with_stream(stream_cb: Callable[[dict[str, Any]], None], openai_comp_api_key: str, messages: list[dict[str, Any]], model: str = "deepseek-chat", openai_comp_api_base_url: str = "https://api.deepseek.com/chat/completions") -> dict[str, Any]:
        """
        Send a request to the OpenAI Compatible API with stream.

        Args:
            stream_cb (Callable[[dict[str, Any]], None]): The callback function for stream.
            openai_comp_api_key (str): The OpenAI Compatible API key.
            messages (list[dict[str, Any]]): The messages to send.
            model (str): The model to use.
            openai_comp_api_base_url (str): The OpenAI Compatible API base URL.

        Returns:
            dict[str, Any]: The response from the OpenAI Compatible API.
        """

        # Send a request to the OpenAI Compatible API
        res: requests.Response = requests.post(
            openai_comp_api_base_url,
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_comp_api_key}"
            },
            json = {
                "model": model,
                "stream": True,
                "messages": messages
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
            'model': model,
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

    def __init__(self, openai_comp_api_key: str, model: str = "deepseek-chat", openai_comp_api_base_url: str = "https://api.deepseek.com/chat/completions") -> None:
        """
        Initialize the Summarizer object.

        Args:
            openai_comp_api_key (str): The OpenAI Compatible API key.
            model (str): The model to use.
            openai_comp_api_base_url (str): The OpenAI Compatible API base URL.

        Returns:
            None
        """
        
        # Set the attributes of the Summarizer object
        self.model: str = model
        self.openai_comp_api_key: str = openai_comp_api_key
        self.openai_comp_api_base_url: str = openai_comp_api_base_url

        # Check the OpenAI Compatible API key
        KeyCheck.check_openai_comp_api_key(openai_comp_api_key, model, openai_comp_api_base_url)

    def summarize(self, u_prompt: str, data: str, stream_cb: Callable[[str], None] = None) -> str:
        """
        Summarize the search results.

        Args:
            u_prompt (str): The prompt of the user.
            data (str): The search results.
            stream_cb (Callable[[str], None]) = None: The callback function for stream. If callback function is not None, the response will be streamed to the callback function as parameters.

        Returns:
            str: The summary of the search results.
        """

        # Create the prompt
        prompt: str = """你是一个专业的AI研究助手，你的核心职责是根据用户提供的查询提示词“{prompt}”、从网络搜索获取的资料“{data}”以及今天的日期和時間“{datetime}”，严格遵循提示词的要求，准确、精炼地总结网络搜索结果。

        任务说明：
        - 理解用户意图：仔细阅读用户给出的提示词，明确用户希望获得什么样的总结——是简洁的要点概括、详细的分析报告、特定问题的答案，还是按照某种格式（如表格、列表）整理信息。
        - 严格基于资料：所有总结内容必须完全来源于提供的数据，不得添加个人知识、猜测或外部信息。若data信息不足，需如实说明，并尽可能基于现有资料给出部分答案或建议。
        - 遵循输出要求：按照提示词中指定的风格、长度、格式（如段落、要点、编号等）组织回答。如果提示词中未明确格式，则以列点或列项的方式组织回答，输出清晰、有条理的文本，便于用户快速获取关键信息。回答中不應該摻雜“根據搜索結果”、“依據搜索結果”等不必要的信息。應該以回答用戶問題的方式來輸出回答。
        - 输出内容要求：回答的内容应符合提示词要求为主，而搜索到的其它资料如果与提示词的搜索主题有关则可以另外列点补充，确保所有相关的信息都在回答中，而不仅限于用户提示词要求的指定搜索主题范围，但与提示词的搜索主题完全无关的内容不得包含。回答根据搜索内容尽可能回答清晰且详细，但不得额外胡乱编造和参杂不实内容。
        - 总结语言要求：总结的语言应与用户的查询提示词“{prompt}”的语言保持一致（例如，用户的查询提示词为中文，则总结使用中文；用户的查询提示词为英文，则总结使用英文）。
        - 保持客观中立：仅陈述事实，不掺杂主观评价或观点。

        示例（仅供理解，实际执行时以用户输入为准）：
        - 用户提示词：“请用三点总结这篇文章的核心观点”，资料为某篇文章的文本。你的输出应为三个要点，概括文章核心。
        - 用户提示词：“根据资料回答：人工智能在医疗领域有哪些应用？”，资料为相关搜索结果。你的输出应直接列出应用领域，并附简短说明。

        现在，请根据用户提供的提示词和数据开始执行任务。"""

        # If callback function is not None
        if stream_cb:
            # Define a function for grabbing the content of the response in stream mode
            def grab_content(res: dict[str, Any]) -> str:
                """
                A function for grabbing the content of the response in stream mode.

                Args:
                    res (dict[str, Any]): The response from the OpenAI Compatible API.

                Returns:
                    None
                """

                return stream_cb(res["choices"][0]["delta"]["content"] if res["choices"][0]["delta"]["content"] else '')

            # Send a request to the OpenAI Compatible API in stream mode
            res: dict[str, Any] = Summarizer.__send_request_with_stream(
                grab_content,
                self.openai_comp_api_key,
                [
                    {
                        "role": "user",
                        "content": prompt.format(prompt = u_prompt, data = data, datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    }
                ],
                self.model,
                self.openai_comp_api_base_url
            )
        else:
            # Send a request to the OpenAI Compatible API in non-stream mode
            res: dict[str, Any] = Summarizer.__send_request(
                self.openai_comp_api_key,
                [
                    {
                        "role": "user",
                        "content": prompt.format(prompt = u_prompt, data = data, datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    }
                ],
                self.model,
                self.openai_comp_api_base_url
            )

        # Return the summary
        return res["choices"][0]["message"]["content"]