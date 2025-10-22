import os
import sys
from pathlib import Path

# Add parent directory to path so we can import thinagents
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ["GEMINI_API_KEY"] = "AIzaSyDACUGxj1NShM0fOMZx91U4sPc4wz0ALf0"
from thinagents import Agent, tool
from pydantic import BaseModel, Field


class AddInput(BaseModel):
    a: int = Field(description="The first number to add")
    b: int = Field(description="The second number to add")

@tool(pydantic_schema=AddInput)
def add(a, b):
    """Add two numbers together"""
    return a + b

def sub(a, b):
    return a - b

greet_agent = Agent(
    name="Greet Agent",
    model="gemini/gemini-2.0-flash",
    prompt="Greet the User and tell that the user is seeing this from the Green Agent"
)

root_agent = Agent(
    name="Root Agent",
    model="gemini/gemini-2.0-flash",
    tools=[add, sub],
    sub_agents=[greet_agent],
    prompt="You are a root agent that can use the add and sub tools to add and subtract numbers and greet user"
)