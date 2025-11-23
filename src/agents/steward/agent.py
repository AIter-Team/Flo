from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt

from src.agents.state import State
from src.config.agents import STEWARD
from src.tools import (
    check_available_instructions,
    get_current_time,
    get_task_instruction,
    handoff_to_agent,
)

steward = create_agent(
    name="steward",
    model=STEWARD.last,
    tools=[
        # Essential tools
        get_current_time,
        get_task_instruction,
        check_available_instructions,
        handoff_to_agent,
        # Steward tools
    ],
)
