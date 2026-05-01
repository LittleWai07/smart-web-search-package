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
from SmartWebSearch.AIModel import AIModel
from SmartWebSearch.Progress import _ProgressData, ProgressStatusSelector as pss
from langid import classify

# Summarizer Class
class Summarizer:
    """
    A class for summarizing the search results.
    """

    # Constants
    COMPLETION_ENDED: str = '[COMPLETION_ENDED]'

    def __init__(self, ai_model: AIModel) -> None:
        """
        Initialize the Summarizer object.

        Args:
            ai_model (AIModel): The AIModel object.

        Returns:
            None
        """
        
        # Set the attributes of the Summarizer object
        self.ai_model: AIModel = ai_model

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
        prompt: str = """你是一个专业的AI研究助手，你的核心职责是根据用户提供的查询提示词“{prompt}”、从网络搜索获取的资料“{data}”以及今天的日期和时间“{datetime}”，严格遵循提示词的要求，准确、精炼地总结网络搜索结果。

        任务说明：
        - 理解用户意图：仔细阅读用户给出的提示词，明确用户希望获得什么样的总结——是简洁的要点概括、详细的分析报告、特定问题的答案，还是按照某种格式（如表格、列表）整理信息。
        - 严格基于资料：所有总结内容必须完全来源于提供的数据，不得添加个人知识、猜测或外部信息。若没有相关资料、资料不足或者与提示词无关，需如实说明资料不足或者与提示词无关，不能根据你的个人知识或猜测给出答案。
        - 资料混乱与准确性：如果资料结构过于混乱、可能出现前后文冲突等不准确问题，则跳过这些不准确的资料，继续总结其他准确的资料。
        - 遵循输出要求：按照提示词中指定的风格、长度、格式（如段落、要点、编号等）组织回答。如果提示词中未明确格式，则以列点或列项的方式组织回答，输出清晰、有条理的文本，便于用户快速获取关键信息。回答中不得包含“根据搜索结果”、“依据搜索结果”、“根据提供的资料”、“Based on the search results”, “Based on the provided information”等“根据搜索结果资料”的相关提示。应该以直接回答用户问题的方式来输出回答。
        - 输出内容要求：回答的内容应符合提示词要求为主，而搜索到的其它资料如果与提示词的搜索主题有关则可以另外列点补充，确保所有相关的信息都在回答中，而不仅限于用户提示词要求的指定搜索主题范围，但与提示词的搜索主题完全无关的内容不得包含。回答根据搜索内容尽可能回答清晰且详细，但不得额外胡乱编造和参杂不实内容。
        - 总结语言要求：总结的语言必须为{lang}，以确保输出语言与用户提示词的语言一致。
        - 保持客观中立：仅陈述事实，不掺杂主观评价或观点。

        示例（仅供理解，实际执行时以用户输入为准）：
        - 用户提示词：“请用三点总结这篇文章的核心观点”，资料为某篇文章的文本。你的输出应为三个要点，概括文章核心。而且由于用户提示词是“中文”的，所以必须以“中文”输出回答。
        - 用户提示词：“人工智能在医疗领域有哪些应用？”，资料为相关搜索结果。你的输出应直接列出应用领域，并附简短说明。而且由于用户提示词是“中文”的，所以必须以“中文”输出回答。
        - 用戶提示词：“What is API?”，资料為一個 API 的定义、用法和范例。你的输出应该列出相关内容并说明。而且由于用户提示词是“英文”的，所以必须以“英文”输出回答。例如：“API is a set of rules or protocols that allow different software components to communicate with each other ...”
        - 用戶提示词：“What is Python and what is it used for?”，资料为一个关于Python的介绍、用途和例子。你的输出应该列出相关内容并说明。而且由于用户提示词是“英文”的，所以必须以“英文”输出回答。
        
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

                # If choices in the response is empty, return an empty string
                if not res["choices"]:
                    return ''
                
                # If delta in the first choice is empty, return an empty string
                if not res["choices"][0].get("delta"):
                    return ''
                
                # If content not in the delta of the first choice, return an empty string
                if not res["choices"][0]["delta"].get("content"):
                    return ''

                # Return the content
                return stream_cb(res["choices"][0]["delta"]["content"] if res["choices"][0]["delta"]["content"] else '')
            
            # Register a progress listener, if the status is pss.STREAM_ENDED then call stream_cb with value self.COMPLETION_ENDED
            listener: Callable[[_ProgressData], None] = lambda pg_data: stream_cb(self.COMPLETION_ENDED) if pg_data.status == pss.STREAM_ENDED else None
            self.ai_model.progress.add_progress_listener(listener)

            # Send a request to the OpenAI Compatible API in stream mode
            res: dict[str, Any] = self.ai_model.send_request_stream(
                [
                    {
                        "role": "user",
                        "content": prompt.format(prompt = u_prompt, data = data, datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S"), lang = classify(u_prompt)[0])
                    }
                ],
                grab_content
            )

            # Unregister the progress listener
            self.ai_model.progress.remove_progress_listener(listener)

        else:
            # Send a request to the OpenAI Compatible API in non-stream mode
            res: dict[str, Any] = self.ai_model.send_request(
                [
                    {
                        "role": "user",
                        "content": prompt.format(prompt = u_prompt, data = data, datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S"), lang = classify(u_prompt))
                    }
                ]
            )

        # Return the summary
        return res["choices"][0]["message"]["content"]