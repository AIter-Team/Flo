from langchain.messages import ToolMessage
from langchain.tools import BaseTool, InjectedState, InjectedToolCallId, tool
from langgraph.types import Command
from typing_extensions import Annotated

from src.agents.root.state import State


@tool("transfer_to_agent", description="Handoff control to another agent")
def handoff_to_agent(
    agent_name: str,
    state: Annotated[State, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    tool_message = ToolMessage(
        content=f"Successfully transferred to {agent_name}",
        name="transfer_to_agent",
        tool_call_id=tool_call_id,
    )
    if agent_name == "root_agent":
        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update={
                "messages": state.messages + [tool_message],
                "active_agent": agent_name,
            },
        )
    else:
        return Command(
            goto=agent_name,
            update={
                "messages": state.messages + [tool_message],
                "active_agent": agent_name,
        },
    )
