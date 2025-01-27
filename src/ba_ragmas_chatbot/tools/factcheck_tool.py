import os
import re

import yaml
from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from duckduckgo_api_haystack import DuckduckgoApiWebSearch
import ollama
import chromadb

class FactCheckToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="The text containing facts to be checked.")

class FactCheckTool(BaseTool):
    name: str = "fact_check_tool"
    description: str = (
        "This tool allows agents to verify facts over the internet, and adds a source to the text if they are true."
    )
    args_schema: Type[BaseModel] = FactCheckToolInput

    def get_llm(self) -> str:
        base_dir =  os.path.dirname(__file__)
        root_dir = os.path.dirname(base_dir)
        yaml_file = os.path.join(root_dir, "config", "configs.yaml")
        with open(yaml_file, 'r') as file:
            config = yaml.safe_load(file)
        llm_name = config['chatbot']['llm']['name']

    def _run(self, argument: str) -> str:
        paragraphs = argument.split("\n\n")
        revised_paragraphs = []
        sources = []

        for paragraph in paragraphs:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            updated_sentences = []

            for sentence in sentences:
                if any(char.isdigit() for char in sentence):
                    facts = [sentence]
                    verified_facts = self.fact_check_with_duckduckgo(facts)

                    result = verified_facts[0]
                    if result["status"] == "verified":
                        updated_sentences.append(f"{sentence} (Source: {result['source']})")
                        sources.append(result['source'])
                    else:
                        continue
                else:
                    updated_sentences.append(sentence)
            revised_paragraphs.append(". ".join(updated_sentences).strip())
        revised_article = "\n\n".join(revised_paragraphs)
        sources_section = "\n\nSources:\n" + "\n".join(set(sources))
        return revised_article + sources_section

    def fact_check_with_duckduckgo(self, facts: List[str]) -> List[dict]:
        """Fact-check each statement using DuckDuckGo."""
        verified = []
        print(facts)
        for fact in facts:
            search_result = self.search_duckduckgo(fact)
            if search_result is not None:
                verified.append({"fact": fact, "status": "verified", "source": search_result})
            else:
                verified.append({"fact": fact, "status": "unverifiable"})
        return verified


    def search_duckduckgo(self, query: str) -> Optional[str]:
        """Query DuckDuckGo for a fact and extract reliable snippets."""
        websearch = DuckduckgoApiWebSearch(top_k=10)
        results = websearch.run(query=query)

        documents = results["documents"]
        links = results["links"]

        return self.do_rag(documents, links, query)

    def do_rag(self, documents: [], links: [], prompt: str)-> Optional[str]:
        client = chromadb.Client()

        for d, l in documents, links:
            output = ollama.generate(
                model=self.get_llm(),
                prompt=f"Using this data: {d}. Check if this is true or false: {prompt}. If it is true, reply with 'yes', if it is false, reply with 'no'."
            )
            print(str(output))
            if str(output).lower() == "yes":
                return l
        return None

