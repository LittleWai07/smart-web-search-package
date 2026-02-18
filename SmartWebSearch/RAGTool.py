"""
SmartWebSearch.RAGTool
~~~~~~~~~~~~

This module implements the RAGTool.
"""

# Import the required modules
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Any
from SmartWebSearch.Debugger import show_debug

class _KnowledgeBase:
    """
    A class for managing a knowledge base.
    """

    def __init__(self, knowledge_base: list[str], knowledge_vector: np.ndarray) -> None:
        """
        Initialize the KnowledgeBase object.

        Args:
            knowledge_base (list[str]): The knowledge base.
            knowledge_vector (np.ndarray): The knowledge vectors.

        Returns:
            None
        """
        self.knowledge_base: list[str] = knowledge_base
        self.knowledge_vector: np.ndarray = knowledge_vector

    def match_knowledge(self, embedding_model: SentenceTransformer, prompt: str, top_k: int = 10, threshold_score: float = 1):
        """
        Match the prompt with the knowledge base.

        Args:
            embedding_model (SentenceTransformer): The embedding model.
            prompt (str): The prompt to be matched.
            top_k (int) = 10: The number of top matches to return.
            threshold_score (float) = 1: The threshold score for a match.

        Returns:
            list[tuple[float, str]]: The top matches with their scores and the corresponding chunks.
        """

        # Encode the prompt into a vector
        prompt_vector: np.ndarray = embedding_model.encode(prompt)

        # Loop through the knowledge base and find the top matches
        matches: list[tuple[float, str]] = []
        for i, knowledge_vector in enumerate(self.knowledge_vector):
            score: float = np.dot(knowledge_vector, prompt_vector)
            matches.append((score, self.knowledge_base[i].strip()))

        # Sort the matches by score
        matches.sort(key = lambda knowledge: knowledge[0], reverse = True)

        # Return the top matches with a threshold score
        return [match for match in matches[:top_k] if match[0] > threshold_score]

class _KnowledgeBaseSet:
    """
    A class for managing a knowledge base set.
    """

    def __init__(self, knowledge_base_set: list[_KnowledgeBase]) -> None:
        """
        Initialize the KnowledgeBaseSet object.

        Args:
            knowledge_base_set (list[_KnowledgeBase]): The knowledge base set.

        Returns:
            None
        """
        self.knowledge_base_set: list[_KnowledgeBase] = knowledge_base_set

    def match_knowledge(self, embedding_model: SentenceTransformer, prompt: str, top_k: int = 10, threshold_score: float = 0.57):
        """
        Match the prompt with the knowledge base set.

        Args:
            embedding_model (SentenceTransformer): The embedding model.
            prompt (str): The prompt to be matched.
            top_k (int) = 10: The number of top matches to return.
            threshold_score (float) = 0.57: The threshold score for a match.

        Returns:
            list[tuple[float, str]]: The top matches with their scores and the corresponding chunks.
        """

        # Match the prompt with the knowledge base set
        matches: list[tuple[float, str]] = []
        for knowledge_base in self.knowledge_base_set:
            matches.extend(knowledge_base.match_knowledge(embedding_model, prompt, top_k, threshold_score))

        # Sort the matches by score
        matches.sort(key = lambda knowledge: knowledge[0], reverse = True)

        # Return the top matches
        return [match for match in matches[:top_k + 5]]

# The RAGTool class
class RAGTool:
    """
    A class for RAG (Retrieval-Augmented Generation).
    """

    @staticmethod
    def __build_knowledge_base(text_data: str, embedding_model: SentenceTransformer, text_splitter: RecursiveCharacterTextSplitter) -> _KnowledgeBaseSet:
        """
        Build the knowledge base from the text data.

        Args:
            text_data (str): The text data to be used as knowledge.

        Returns:
            _KnowledgeBaseSet: The knowledge base set.
        """

        # Split the text data into chunks
        chunks: list[str] = text_splitter.split_text(text_data)

        # Remove the double spaces and newlines
        for idx, chunk in enumerate(chunks):
            while '  ' in chunks[idx]:
                chunks[idx] = chunks[idx].replace('  ', ' ')
            while '\n ' in chunks[idx]:
                chunks[idx] = chunks[idx].replace('\n ', '\n')
            while '\n\n' in chunks[idx]:
                chunks[idx] = chunks[idx].replace('\n\n', '\n')

        # Remove the chunks with less than 100 characters
        chunks: list[str] = [chunk for chunk in chunks if len(chunk) > 100]

        # Remove the chunks includes enabling javascript
        chunks: list[str] = [chunk for chunk in chunks if 'enable' not in chunk.lower() or 'javascript' not in chunk.lower()]

        # Remove the chunks includes enabling cookies
        chunks: list[str] = [chunk for chunk in chunks if 'enable' not in chunk.lower() or 'cookie' not in chunk.lower()]

        # Remove the chunks includes verifying humans
        chunks: list[str] = [chunk for chunk in chunks if 'verify' not in chunk.lower() or 'human' not in chunk.lower()]

        # Seperate the chunks into several chunk sets every 30 chunks
        chunk_sets: list[list[str]] = [chunks[i: i + 30] for i in range(0, len(chunks), 30)]

        # Encode the chunk sets into vector sets
        knowledge_vector_set: list[np.ndarray] = []
        for idx, chunk_set in enumerate(chunk_sets, start = 1):
            show_debug(f"Creating knowledge base set {idx}/{len(chunk_sets)}...")
            knowledge_vector_set.append(embedding_model.encode(chunk_set))
        
        show_debug(f"Knowledge base set created.")

        # Create knowledge base objects for each set
        knowledge_base_set: list[_KnowledgeBase] = [_KnowledgeBase(chunk_set, knowledge_vector_set) for chunk_set, knowledge_vector_set in zip(chunk_sets, knowledge_vector_set)]

        # Create a knowledge base set object
        knowledge_base_set: _KnowledgeBaseSet = _KnowledgeBaseSet(knowledge_base_set)

        return knowledge_base_set

    def __init__(self, embedding_model_name: str = 'BAAI/bge-m3') -> None:
        """
        Initialize the RAGTool object.
        
        Args:
            embedding_model_name (str) = 'BAAI/bge-m3': The name of the embedding model.
        
        Returns:
            None
        """

        # Initialize the text splitter
        self.text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
            chunk_size = 600,
            chunk_overlap = 80
        )

        # Initialize the SentenceTransformer model
        self.embedding_model: SentenceTransformer = SentenceTransformer(embedding_model_name)

    def build_knowledge(self, text_data: str) -> _KnowledgeBaseSet:
        """
        Build the knowledge base from the text data.

        Args:
            text_data (str): The text data to be used as knowledge.

        Returns:
            _KnowledgeBaseSet: The knowledge base set.
        """

        # Build the knowledge base
        knowledge_base_set: _KnowledgeBaseSet = self.__build_knowledge_base(text_data, self.embedding_model, self.text_splitter)

        return knowledge_base_set

    def match_knowledge(self, knowledge_base: _KnowledgeBase | _KnowledgeBaseSet, prompt: str, top_k: int = 10, threshold_score: float = 0.57) -> list[tuple[float, str]]:
        """
        Match the prompt with the knowledge base.

        Args:
            knowledge_base (_KnowledgeBase | _KnowledgeBaseSet): The knowledge base.
            prompt (str): The prompt to be matched.
            top_k (int) = 10: The number of top matches to return.
            threshold_score (float) = 0.57: The threshold score for the top matches.

        Returns:
            list[tuple[float, str]]: The top matches with their scores and the corresponding chunks.
        """

        # Match the prompt with the knowledge base
        return knowledge_base.match_knowledge(self.embedding_model, prompt, top_k, threshold_score)