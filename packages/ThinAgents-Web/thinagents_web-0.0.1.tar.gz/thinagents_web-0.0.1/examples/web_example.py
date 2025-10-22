import os
import sys
from pathlib import Path

os.environ["GEMINI_API_KEY"] = "AIzaSyDACUGxj1NShM0fOMZx91U4sPc4wz0ALf0"

# Import from installed thinagents package
from thinagents import Agent, tool
from pydantic import BaseModel, Field

# Add parent directory to path to import local thinagents.web
sys.path.insert(0, str(Path(__file__).parent.parent))
from thinagents.web import WebUI


class AddInput(BaseModel):
    a: int = Field(description="The first number to add")
    b: int = Field(description="The second number to add")


@tool(pydantic_schema=AddInput)
def add(a, b):
    """Add two numbers together"""
    return a + b


def sub(a, b):
    """Subtract two numbers"""
    return a - b


greet_agent = Agent(
    name="Greet Agent",
    model="gemini/gemini-2.0-flash",
    prompt="Greet the User and tell that the user is seeing this from the Greet Agent"
)

root_agent = Agent(
    name="Root Agent",
    model="gemini/gemini-2.0-flash",
    tools=[add, sub],
    sub_agents=[greet_agent],
    prompt="You are a helpful assistant that can use tools to add and subtract numbers, and you can delegate to other agents to greet users."
)

if __name__ == "__main__":
    WebUI(root_agent).run()
    
    # Dev mode (if you have frontend source):
    # WebUI(root_agent, dev_mode=True).run()
    
    # Custom port:
    # WebUI(root_agent, port=8080).run()

