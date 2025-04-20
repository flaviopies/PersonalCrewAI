from langchain_community.utilities import GoogleSerperAPIWrapper
from crewai.tools import BaseTool
from dotenv import load_dotenv
from typing import Optional
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize tools
class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = "Useful for searching the web for current information. Input should be a search query."
    search: Optional[GoogleSerperAPIWrapper] = None

    def __init__(self):
        super().__init__()
        # Initialize Serper with API key from environment variables
        self.search = GoogleSerperAPIWrapper(serper_api_key=os.getenv('SERPER_API_KEY'))

    def _run(self, query: str) -> str:
        """Execute the web search with focus on current and future events."""
        try:
            # Add temporal context to the query
            current_year = datetime.now().year
            next_year = current_year + 1
            temporal_query = f"{query} (2024 OR 2025) site:.br"
            
            # Perform the search
            results = self.search.run(temporal_query)
            
            # If no specific results found, try a more general search
            if not results or "no results" in results.lower():
                return self.search.run(query + " site:.br")
            
            return results
        except Exception as e:
            return f"Error performing web search: {str(e)}"

# Create tool instance
search_tool = WebSearchTool()

# Agent configurations
AGENT_CONFIGS = {
    'manager': {
        'role': 'Personal Assistant Manager',
        'goal': 'Coordinate and delegate tasks to specialized agents based on user needs, focusing on providing accurate and current information',
        'backstory': """You are an experienced personal assistant manager who excels at understanding user needs 
        and delegating tasks to the right specialists. You maintain a professional yet friendly tone and 
        ensure all tasks are completed efficiently. You always verify dates and information to ensure they are current and accurate.""",
        'verbose': True,
        'allow_delegation': True,
        'tools': [search_tool]
    },
    'researcher': {
        'role': 'Research Specialist',
        'goal': 'Gather and analyze current information from various sources, ensuring accuracy of dates and details',
        'backstory': """You are a detail-oriented research specialist who excels at finding accurate and 
        relevant information. You verify sources and provide comprehensive summaries, with special attention 
        to ensuring dates and event information are current and accurate.""",
        'verbose': True,
        'tools': [search_tool]
    },
    'planner': {
        'role': 'Planning Specialist',
        'goal': 'Help organize and plan tasks and schedules with current and accurate information',
        'backstory': """You are an expert in organization and planning. You help break down complex tasks 
        into manageable steps and create efficient schedules. You always verify that event information 
        and dates are current and accurate.""",
        'verbose': True,
        'tools': [search_tool]
    }
} 