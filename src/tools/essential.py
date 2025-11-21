import os
from datetime import datetime
from typing_extensions import Annotated, Any


from langchain.messages import ToolMessage
from langchain.tools import InjectedState, InjectedToolCallId, tool
from langgraph.types import Command
from langchain.tools import tool
from langgraph.config import get_stream_writer

from src.config import MEMORY_DIR
from src.agents.state import State


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


@tool
def get_task_instruction(task_name: str) -> dict[str, str]:
    """
    Tool for getting task instruction

    Args:
        task_name (str): Task name

    Returns:
        dict: A dictionary containing the instruction text.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'task_instruction' key.
              If 'error', includes an 'error_message' key.
    """
    writer = get_stream_writer()
    instruction_path = os.path.join(MEMORY_DIR, f"procedural/{task_name}.txt")

    writer(f"Retrieving `{task_name}` task instruction..")
    if os.path.exists(instruction_path):
        with open(instruction_path, "r") as file:
            return {"status": "success", "task_instruction": file.read()}
    else:
        return {
            "status": "error",
            "error_message": "There is an error while retrieving file",
        }


@tool
def check_available_instruction() -> dict[str, Any]:
    """
    Tool for checking available task instruction

    Returns:
        dict: A dictionary containing the instruction text.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'task_instruction' key.
              If 'error', includes an 'error_message' key.
    """
    instruction = []
    writer = get_stream_writer()

    instruction_path = os.path.join(MEMORY_DIR, "procedural")



    if os.path.exists(instruction_path):
        writer(f"Retrieving all available instruction..")
        for dir in os.scandir(instruction_path):
            instruction.append(dir.name.split('.')[0])

        return {
            "status": "success",
            "instruction_list": instruction
        }
    else:
        return {
            "status": "error",
            "error_message": "There is an error while retrieving file",
        }


@tool
def get_current_time() -> dict:
    """Get current time

    Returns:
        dict: A dictionary containing current timestamp.
    """
    writer = get_stream_writer()
    writer("Retrieving current time..")
    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
