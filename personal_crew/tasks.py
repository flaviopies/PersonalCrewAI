from crewai import Task

def create_main_task(user_input, manager_agent):
    """Create the main task for the manager agent."""
    return Task(
        description=f"""As the manager, analyze this request and coordinate with the appropriate agents:
        {user_input}
        
        Break down the request into specific tasks and delegate them to the appropriate agents.
        Ensure all aspects of the request are addressed and provide a comprehensive response.""",
        expected_output="""A detailed response that addresses all aspects of the user's request, 
        including any research findings, plans, or recommendations. The response should be well-structured 
        and easy to understand.""",
        agent=manager_agent
    ) 