from langchain.messages import ToolMessage
from langchain.tools import BaseTool, InjectedState, InjectedToolCallId, tool
from langgraph.types import Command
from typing_extensions import Annotated

from src.agents.root.state import State


def create_handoff_tool(
    *, agent_name: str, name: str | None = None, description: str | None = None
) -> BaseTool:
    if name is None:
        name = f"transfer_to_{agent_name}"
    if description is None:
        description = f"Ask agent '{agent_name}' for help"

    @tool(name, description=description)
    def handoff_to_agent(
        state: Annotated[State, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        tool_message = ToolMessage(
            content=f"Successfully transferred to {agent_name}",
            name=name,
            tool_call_id=tool_call_id,
        )
        return Command(
            goto=agent_name,
            # graph=Command.PARENT,
            update={
                "messages": state.messages + [tool_message],
                "active_agent": agent_name,
            },
        )

    return handoff_to_agent


@tool("transfer_to_root_agent", description="Handoff control back to the root agent")
def handoff_to_root_agent(
    state: Annotated[State, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    tool_message = ToolMessage(
        content=f"Successfully transferred to root agent",
        name="transfer_to_root_agent",
        tool_call_id=tool_call_id,
    )
    return Command(
        goto="root_agent",
        graph=Command.PARENT,
        update={
            "messages": state.messages + [tool_message],
            "active_agent": "root_agent",
        },
    )
