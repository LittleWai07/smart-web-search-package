"""
SmartWebSearch.QueryStorm
~~~~~~~~~~~~

This module implements the query brainstorm for the web searching module.
"""

# Import the required modules
from typing import Any
import requests
from SmartWebSearch.KeyCheck import KeyCheck

# QueryStorm Class
class QueryStorm:
    """
    A class for query brainstorming.
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

    def __init__(self, openai_comp_api_key: str, model: str = "deepseek-chat", openai_comp_api_base_url: str = "https://api.deepseek.com/chat/completions") -> None:
        """
        Initialize the QueryStorm object.

        Args:
            openai_comp_api_key (str): The OpenAI Compatible API key.
            openai_comp_api_base_url (str): The OpenAI Compatible API base URL.

        Returns:
            None
        """

        # Set the attributes of the QueryStorm object
        self.model: str = model
        self.openai_comp_api_key: str = openai_comp_api_key
        self.openai_comp_api_base_url: str = openai_comp_api_base_url

        # Check the OpenAI Compatible API key
        KeyCheck.check_openai_comp_api_key(openai_comp_api_key, model, openai_comp_api_base_url)

    def decompose_tasks_with_prompt(self, u_prompt: str) -> list[str]:
        """
        Decompose task prompts based on the user prompt.

        Args:
            u_prompt (str): The user prompt.

        Returns:
            list[str]: The generated task prompts.
        """

        prompt: str = """你是一个专业的搜索任务分解助手。你的工作是将用户给出的包含多个搜索需求的提示词，分解成多个独立的搜索任务提示词。

        任务描述
        用户会输入一段提示词{prompt}，其中可能包含一个或多个搜索请求，每个请求针对不同的主体（如人物、团体、事物等）。你需要识别出每个独立的主体，并为每个主体生成一个对应的搜索任务提示词。如果一个主体下用户要求搜索多个方面的内容（如简介、成员、专辑等），则将这些内容整合到同一个任务提示词中。

        输出格式
        - 每个任务提示词的格式为：“搜索关于[主体]的[具体搜索范围]”
        - 如果用户没有指定具体搜索范围，则使用“资料”作为默认范围。
        - 如果有多个任务，请用“&&”将每个任务提示词连接起来。
        - 如果只有一个任务，直接输出该任务提示词，不加“&&”。
        - 输出时不要包含任何其他解释或文字，只输出格式化后的任务提示词字符串。
        - 根据用户提示词所用的语言不同，输出结果也要按照提示词所用的语言输出。

        示例
        示例1：
        用户输入：搜索关于IVE这个KPOP组合的资料，关于IVE的简介、成员、专辑和歌曲。此外，帮我搜索关于ATEEZ这个KPOP组合的资料，关于ATEEZ的成员、专辑和歌曲。
        你的输出：搜索IVE这个KPOP组合的简介、成员、专辑和歌曲&&搜索ATEEZ这个KPOP组合的成员、专辑和歌曲

        示例2：
        用户输入：搜索关于IVE这个KPOP组合的资料，关于IVE的简介、成员、专辑和歌曲。此外，帮我搜索关于ATEEZ这个KPOP组合的资料，关于ATEEZ的成员、专辑和歌曲。另外，还有关于HoneyWorks这个日本组合的资料
        你的输出：搜索IVE这个KPOP组合的简介、成员、专辑和歌曲&&搜索ATEEZ这个KPOP组合的成员、专辑和歌曲&&搜索HoneyWorks这个日本组合的资料

        示例3：
        用户输入：搜索关于IVE这个KPOP组合的资料
        你的输出：搜索IVE这个KPOP组合的资料

        注意事项
        - 仔细阅读用户输入，识别出所有不同的搜索主体。
        - 每个主体对应一个任务，即使对同一个主体有多个描述，也只生成一个任务提示词。
        - 任务提示词应准确反映用户要求搜索的具体内容，尽量保留用户的原词。
        - 如果用户对某个主体没有指定具体范围，则使用“资料”概括。
        - 确保输出格式严格遵循要求：多个任务用“&&”分隔。
        
        请严格按照上述格式和示例执行。"""

        # Decompose the prompt into task prompts
        res: dict[str, Any] = self.__send_request(
            self.openai_comp_api_key,
            [
                {
                    "role": "user",
                    "content": prompt.format(prompt = u_prompt)
                }
            ],
            self.model,
            self.openai_comp_api_base_url
        )

        # Return the decomposed task prompts
        return [ i.strip() for i in res["choices"][0]["message"]["content"].split("&&") ]

    def storm_with_summary(self, prompt: str, summary: str) -> list[str]:
        """
        Generate auxiliary queries based on the prompt and summary of the search results.

        Args:
            prompt (str): The prompt.
            summary (str): The summary of the search results.

        Returns:
            list[str]: The generated queries. (Auxiliary Queries)
        """

        prompt: str = """你是一个智能搜索助手，专门负责分析用户的搜索意图并生成扩展的搜索辅助关键词。

        任务描述：
        根据用户提供的提示詞“{prompt}”和提示詞相關关键词的搜索结果总结“{summary}”，首先判断用户想搜索的内容的核心类型（例如，概念定义、工具使用、历史背景、技术原理等），然后基于这个类型，延展出更多相关的搜索辅助关键词。这些关键词应帮助用户进一步精确搜索，获取更具体、更深入的信息。

        输出格式要求：
        - 输出1至3个搜索辅助关键词即可，不必太多，也不能太少。
        - 仅输出搜索辅助关键词，不包含任何其他文字或解释。
        - 每个搜索辅助关键词之间用一个空格“ ”隔开。
        - 如果搜索辅助关键词内包含多个单词，请用加号“+”连接，不要使用空格或其他分隔符。
        - 关键词的语言应与用户提示词的语言保持一致（例如，用户提示词为中文，则关键词使用中文；用户提示词为英文，则关键词使用英文），以确保搜索结果的相关性。

        示例：
        输入：
        prompt = 什麽是三角函数？
        summary = 三角函数是数学很常见的一类关于角度的函数。三角函数将直角三角形的内角和它的两边的比值相关联，亦可以用单位圆的各种有关线段的长短的等价来定义。三角函数在研究三角形和圆形等几何形状的性质时有着重要的作用，亦是研究振动、波、天体运动和各种周期性现象的基础数学工具。在数学分析上，三角函数亦定义为无穷级数或特定微分方程式的解，允许它们的取值扩展到任意实数值，甚至是复数值。
        输出：
        definitions purposes general+formulas

        请严格按照上述格式和示例执行。"""

        # Generate queries based on the summary of the search results
        res: dict[str, Any] = self.__send_request(
            self.openai_comp_api_key,
            [
                {
                    "role": "user",
                    "content": prompt.format(prompt = prompt, summary = summary)
                }
            ],
            self.model,
            self.openai_comp_api_base_url
        )

        # Return the generated queries
        return res["choices"][0]["message"]["content"].split(" ")
    
    def storm_with_prompt(self, u_prompt: str) -> list[str]:
        """
        Generate a query based on the prompt.

        Args:
            u_prompt (str): The user prompt.

        Returns:
            list[str]: The generated queries. (Main Queries, Auxiliary Queries)
        """

        prompt: str = """你是一个专业的搜索关键词优化助手，擅长分析用户的查询意图，并提取精准的网络搜索关键词。

        任务描述：
        根据用户提供的提示词 {prompt}，判断用户想要搜索的核心内容，并列出网络搜索关键词。
        关键词生成规则：
        - 主要关键词：准确反映搜索主题的核心概念，必须保留。
        - 辅助关键词：围绕主要关键词，涵盖用户明确提及需要搜索的具体内容（例如定义、类型、用途、原理、历史、相关公式或操作方法等）。
        - 输出长度规则：
        - 如果用户仅提出核心搜索主题，未明确要求搜索任何具体内容，则只输出主要关键词。
        - 如果用户在提示词中明确指明需要搜索与核心主题相关的具体内容，则输出「主要关键词 + 辅助关键词」，且辅助关键词数量不超过3个。
        - 关键词语言：关键词的语言应与用户提示词的语言保持一致（例如，用户提示词为中文，则关键词使用中文；用户提示词为英文，则关键词使用英文），以确保搜索结果的相关性。
        
        输出格式要求：
        - 仅输出关键词本身，不包含任何解释或附加文字。
        - 关键词之间用一个空格「 」分隔。
        - 如果一个关键词由多个词语组成，请用加号「+」连接（例如：artificial+intelligence 或 人工智能+应用），以确保该关键词在搜索时被视为一个整体。
        - 第一个关键词始终为主要关键词，若存在辅助关键词则依次排列其后（最多3个）。
        
        示例：
        - 用户提示词：What is trigonometry?（未指定具体内容）
        输出：trigonometric+functions
        - 用户提示词：I want to learn about the definitions and formulas of trigonometry（明确指定内容）
        输出：trigonometric+functions definitions formulas applications （此处“definitions”和“formulas”是用户明确提到的，因此优先纳入）
        
        请严格遵循上述格式，确保输出的关键词准确、简洁，能够帮助用户进行高效的网络搜索。"""

        # Generate a query based on the prompt
        res: dict[str, Any] = self.__send_request(
            self.openai_comp_api_key,
            [
                {
                    "role": "user",
                    "content": prompt.format(prompt = u_prompt)
                }
            ],
            self.model,
            self.openai_comp_api_base_url
        )

        # Return the generated queries
        return res["choices"][0]["message"]["content"].split(" ")