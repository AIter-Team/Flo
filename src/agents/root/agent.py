from dataclasses import dataclass, field

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import Literal

from src.agents.quant import quant_agent
from src.tools.handoffs import create_handoff_tool
from src.utils import client

from .state import State

checkpointer = InMemorySaver()

FLO = client.pull_prompt("flo-root", include_model=True)

tools = [create_handoff_tool(agent_name="quant_agent")]
model = ChatOpenAI(model="gpt-4.1-mini").bind_tools(tools)


async def root_agent(state: State):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            await model.ainvoke(
                [SystemMessage(content=FLO.first.messages[0].prompt.template)]
                + state.messages
            )
        ],
    }


def entry_routing(state: State) -> Literal["quant_agent", "root_agent"]:
    if state.active_agent == "quant_agent":
        return "quant_agent"
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

graph.add_conditional_edges(START, entry_routing, ["quant_agent", "root_agent"])
graph.add_conditional_edges("root_agent", should_continue, ["tool_node", END])

flo = graph.compile(checkpointer=checkpointer)
