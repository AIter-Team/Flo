import uuid

from langchain.tools import ToolRuntime, tool
from typing_extensions import Optional


@tool
def create_financial_goal(
    description: str, deadline: str, notes: Optional[str], runtime: ToolRuntime
):
    """Create and save goal to memory

    Args:
        description (str): Goal description
        deadline (str): Goal deadline in 'YYYY-MM-DD HH:MM:SS' format.
        notes (str): Optional notes specified by the user.

    Returns:
        dict: A dictionary containing the transaction record status.
    """

    writer = runtime.stream_writer
    user_name = runtime.state["user_name"]
    namespace = (user_name, "goals")
    id = uuid.uuid4()
    store = runtime.store

    writer("Creating goals..")
    goal = {
        "description": description,
        "deadline": deadline,
        "status": "in_progress",
        "notes": notes,
    }

    writer("Saving goals..")
    store.put(namespace, id, goal)

    return {
        "status": "success",
        "summary": (
            "Goal created successfully.\n"
            f"Id: {id}\n"
            f"Description: {description}\n"
            f"Deadline: {deadline}\n"
            f"Notes: {notes}\n"
        ),
    }


@tool
def get_all_goals(runtime: ToolRuntime):
    """Get all goals from memory"""
    writer = runtime.stream_writer
    user_name = runtime.state["user_name"]
    namespace = (user_name, "goals")
    store = runtime.store

    writer("Retrieving goals..")
    goals = []

    for goal in store.search(namespace):
        goals.append(
            {
                "id": goal.key,
                "goal": goal.value["description"],
                "deadline": goal.value["deadline"],
                "status": goal.value["status"],
                "notes": goal.value["notes"],
            }
        )

    return {"status": "success", "goals": goals}
