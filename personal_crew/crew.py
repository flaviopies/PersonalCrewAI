from crewai import Crew, Process
from .agents import create_agents
from .tasks import create_main_task

def create_crew(user_input):
    """Create and return a crew with all agents and tasks."""
    # Create all agents
    agents = create_agents()
    
    # Create the main task
    main_task = create_main_task(user_input, agents['manager'])
    
    # Create and return the crew
    return Crew(
        agents=list(agents.values()),
        tasks=[main_task],
        process=Process.sequential,
        verbose=True
    ) 