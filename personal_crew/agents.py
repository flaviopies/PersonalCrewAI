from crewai import Agent
from .config import AGENT_CONFIGS

def create_agents():
    """Create and return all agents with their configurations."""
    agents = {}
    
    for agent_type, config in AGENT_CONFIGS.items():
        agents[agent_type] = Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=config['verbose'],
            allow_delegation=config.get('allow_delegation', False),
            tools=config['tools']
        )
    
    return agents 