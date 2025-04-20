from langchain.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from typing import List

class KnowledgeTools:
    def __init__(self):
        self.search_tool = DuckDuckGoSearchRun()
        
    def get_tools(self) -> List[Tool]:
        """Return a list of available tools for the agents."""
        return [
            Tool(
                name="Web Search",
                func=self.search_tool.run,
                description="Useful for searching the web for current information. Input should be a search query."
            )
        ] 