from dataclasses import dataclass, field

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import Literal

from src.agents.capitalist import capitalist_agent
from src.agents.quant import quant_agent
from src.agents.state import State
from src.tools import handoff_to_agent
from src.utils import client

checkpointer = InMemorySaver()

FLO = client.pull_prompt("flo/flo", include_model=True)

tools = [handoff_to_agent]


async def root_agent(state: State):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            await FLO.last.ainvoke(
                FLO.first.invoke(
                    {
                        "user_currency": "IDR",
                        "user_language": "English",
                        "user_name": "Revito",
                    }
                ).messages
                + state.messages
            )
        ],
    }


def entry_routing(state: State) -> Literal["quant_agent", "capitalist_agent", "root_agent"]:
    if state.active_agent == "quant_agent":
        return "quant_agent"
    elif state.active_agent == "capitalist_agent":
        return "capitalist_agent"
    else:
        return "root_agent"


def should_continue(state: State) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
    last_message = state.messages[-1]

    if last_message.tool_calls:
        return "tool_node"

    return END


graph = StateGraph(State)
graph.add_node("root_agent", root_agent)
graph.add_node("tool_node", ToolNode(tools))
graph.add_node("quant_agent", quant_agent)
graph.add_node("capitalist_agent", capitalist_agent)

graph.add_conditional_edges(START, entry_routing, ["quant_agent", "capitalist_agent", "root_agent"])
graph.add_conditional_edges("root_agent", should_continue, ["tool_node", END])

flo = graph.compile(checkpointer=checkpointer)
