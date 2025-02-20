import os
import yaml
import ollama

from crewai.tools import BaseTool
from typing import Type, Optional

from pydantic import BaseModel, Field
from duckduckgo_api_haystack import DuckduckgoApiWebSearch

class FactCheckToolInput(BaseModel):
    """Input schema for FactCheckTool."""
    argument: str = Field(..., description="The fact that can be true or false.")

class FactCheckTool(BaseTool):
    name: str = "fact_check_tool"
    description: str = (
        "This tool allows agents to verify a fact and returns if it is true or false."
    )
    args_schema: Type[BaseModel] = FactCheckToolInput

    def _run(self, argument: str) -> str:
        is_true, source = self.fact_check_with_duckduckgo(argument)
        if is_true:
            return str(True)
        else:
            return str(False)

    def fact_check_with_duckduckgo(self, fact: str) -> tuple[bool, str] | tuple[bool, None]:
        """Fact-check the statement using DuckDuckGo."""
        search_result = self.search_duckduckgo(fact)
        if search_result is not None:
            return True, search_result
        else:
            return False, None

    def search_duckduckgo(self, query: str) -> Optional[str]:
        """Query DuckDuckGo for a fact and extract reliable snippets."""
        websearch = DuckduckgoApiWebSearch(top_k=10, backend="auto")
        results = websearch.run(query=query)

        documents = results["documents"]
        links = results["links"]

        return self.check_if_true(documents, links, query)

    def check_if_true(self, documents: [], links: [], prompt: str)-> Optional[str]:
        for d, l in zip(documents, links):
            output = ollama.generate(
                model=self.get_llm(),
                prompt=f"Using this data: {d}. Check if this is true or false: {prompt}. If it is true, reply with 'yes', if it is false, reply with 'no'."
            )
            if "yes" in str(output).lower():
                return l
        return None

    def get_llm(self) -> str:
        base_dir = os.path.dirname(__file__)
        root_dir = os.path.dirname(base_dir)
        yaml_file = os.path.join(root_dir, "config", "configs.yaml")
        with open(yaml_file, 'r') as file:
            config = yaml.safe_load(file)
        llm_name = config['chatbot']['llm']['name']
        return llm_name
