from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START
from langgraph.graph.state import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.store.memory import InMemoryStore
from typing_extensions import Literal

# Specialist agents
from src.agents.capitalist import capitalist
from src.agents.quant import quant
from src.agents.state import State
from src.agents.steward import steward
from src.agents.strategist import strategist
from src.config.agents import FLO
from src.tools import handoff_to_agent

checkpointer = InMemorySaver()
store = InMemoryStore()

tools = [handoff_to_agent]


async def root_agent(state: State):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            await FLO.last.ainvoke(
                FLO.first.invoke(
                    {
                        "user_currency": state.user_currency,
                        "user_language": state.user_language,
                        "user_name": state.user_name,
                    }
                ).messages
                + state.messages
            )
        ],
    }


def entry_routing(
    state: State,
) -> Literal["quant", "capitalist", "strategist", "root_agent"]:
    if state.active_agent == "quant":
        return "quant"
    elif state.active_agent == "capitalist":
        return "capitalist"
    elif state.active_agent == "strategist":
        return "strategist"
    elif state.active_agent == "steward":
        return "steward"
    else:
        return "root_agent"


def tool_condition(state: State) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
    last_message = state.messages[-1]

    if last_message.tool_calls:
        return "tool_node"

    return END


graph = StateGraph(State)
graph.add_node("root_agent", root_agent)
graph.add_node("tool_node", ToolNode(tools))
graph.add_node("quant", quant)
graph.add_node("capitalist", capitalist)
graph.add_node("strategist", strategist)
graph.add_node("steward", steward)

graph.add_conditional_edges(
    START, entry_routing, ["quant", "capitalist", "strategist", "steward", "root_agent"]
)
graph.add_conditional_edges("root_agent", tool_condition, ["tool_node", END])

flo = graph.compile(checkpointer=checkpointer, store=store)
