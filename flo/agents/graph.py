from langchain.messages import AIMessage
from langchain.agents import AgentState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import Literal, NotRequired

from .general import general_agent
from .quant import quant_agent

checkpointer = InMemorySaver()


class MainState(AgentState):
    active_agent: NotRequired[str]


def route_after_agent(
    state: MainState,
) -> Literal["general", "quant", "__end__"]:

    messages = state.get("messages", [])

    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
            return "__end__"

    active = state.get("active_agent", "general")
    return active if active else "general"


def route_initial(state: MainState) -> Literal["general", "quant"]:
    return state.get("active_agent") or "general"


graph = StateGraph(MainState)

graph.add_node("general", general_agent)
graph.add_node("quant", quant_agent)

graph.add_conditional_edges(START, route_initial, ["general", "quant"])
graph.add_conditional_edges("general", route_after_agent, ["general", "quant", END])
graph.add_conditional_edges("quant", route_after_agent, ["general", "quant", END])

flo = graph.compile()
