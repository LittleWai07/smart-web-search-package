from setuptools import setup

setup(
   name='SmartWebSearch',
   version='1.2.1',
   description='SmartWebSearch is a Python package that combines the Tavily search API with Retrieval-Augmented Generation (RAG), LLM-powered query expansion, and web content extraction to perform intelligent, deep web searches with automated summarization.',
   author='LIN WAI CHON',
   author_email='jacksonlam.temp@gmail.com',
   packages=['SmartWebSearch'],
   install_requires=["requests", "bs4", "selenium", "markdownify", "tavily", "numpy", "sentence_transformers", "langchain_text_splitters"]
)