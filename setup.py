from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
   long_description = fh.read()

setup(
   name='SmartWebSearch',
   version='1.2.3',
   description='SmartWebSearch is a Python package that combines the Tavily search API with Retrieval-Augmented Generation (RAG), LLM-powered query expansion, and web content extraction to perform intelligent, deep web searches with automated summarization.',
   long_description=long_description,
   long_description_content_type="text/markdown",
   author='LIN WAI CHON',
   author_email='jacksonlam.temp@gmail.com',
   packages=['SmartWebSearch'],
   install_requires=["requests", "bs4", "selenium", "markdownify", "tavily", "numpy", "sentence_transformers", "langchain_text_splitters"]
)